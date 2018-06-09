import base64
import hashlib
import hmac
import logging
import socket
import time
from datetime import datetime, timezone
from http.client import HTTPSConnection
from typing import List, Tuple
from urllib.parse import urlencode

from lxml import objectify

# from base.models import Seller
# Seller { seller_id, access_key, secret_key, mws_url }

logger = logging.getLogger(__name__)

class WMSClient:
    TIMEOUT = 10
    API_SECTIONS = {
        "Reports": {
            "Version": "2009-01-01",
            "Operations": ["GetReport", "GetReportCount",
                           "GetReportList", "GetReportListByNextToken",
                           "GetReportRequestList", "GetReportRequestCount", "GetReportRequestListByNextToken",
                           "CancelReportRequests", "RequestReport",
                           "ManageReportSchedule", "GetReportScheduleList", "GetReportScheduleListByNextToken",
                           "GetReportScheduleCount", "UpdateReportAcknowledgements"],
            "Path": "/Reports/2009-01-01"
        },
        "Feeds": {
            "Version": "2009-01-01",
            "Operations": ["SubmitFeed", "GetFeedSubmissionList", "GetFeedSubmissionResult"],
            "Path": "/Feeds/2009-01-01"
        }
    }

    def __init__(self, seller = None):
        # 必须参数
        self.action = None
        self.aws_access_key_id = None
        self.mws_auth_token = None # 仅适用于网页应用和第三方开发商授权
        self.seller_id = None
        self.signature = None
        self.signature_method = "HmacSHA256"
        self.signature_version = "2"
        self.timestamp = None
        self.version = None

        # 中间变量
        self.body = None
        self.content_md5 = None
        self.sign = None
        self.extra_params = None
        self.common_params = None
        self.params = None
        self.url = None
        self.raw_rsp = None
        self.rsp = None
        self.error = None

        # seller
        self.seller = None
        if seller is not None: self.set_seller(seller)

    def set_seller(self, seller) -> bool:
        self.seller = seller
        self.seller_id = seller.seller_id
        self.aws_access_key_id = seller.access_key
        return True

    def has_error(self) -> bool:
        return self.error != None

    def send_request(self, action: str, extra_params: List[Tuple[str, str]], body=None, max_retry=1) -> bool:
        assert self.seller != None
        self._clear()
        self.body = body
        self.action = action
        self.version = self._get_api_version()
        self._gen_common_params()
        self.extra_params = extra_params
        self.params = self.common_params + self.extra_params
        if self.body != None:
            self._cal_content_md5()
            self._add_content_md5()
        self._add_sign()

        cnt = 0
        while True:
            if self._request(): return True
            time.sleep(1)
            cnt += 1
            if cnt >= max_retry: return False


    def parse_xml_response(self) -> bool:
        try:
            rsp = objectify.fromstring(self.raw_rsp)
        except Exception as e:
            logger.fatal('Parse wms response failed, rsp: %s', self.raw_rsp)
            self.error = ('parse_response_failed', self.raw_rsp)
            return False
        idx = rsp.tag.find('}')
        if idx >= 0: rsp_type = rsp.tag[idx + 1:]
        else: rsp_type = rsp.tag

        if rsp_type == "ErrorResponse":
            logger.error("Recv error response<requestId: %s, Type: %s, Code: %s, Message: %s>",
                       rsp.RequestID, rsp.Error[0].Type, rsp.Error[0].Code, rsp.Error[0].Message)
            self.error = ('error_response',
                          'recv wms error response<%s, %s, %s, %s>',
                          rsp.RequestID, rsp.Error[0].Type, rsp.Error[0].Code, rsp.Error[0].Message)
            return False

        self.rsp = rsp
        return True

    def _clear(self):
        self.body = None
        self.content_md5 = None
        self.sign = None
        self.extra_params = None
        self.common_params = None
        self.params = None
        self.url = None
        self.raw_rsp = None
        self.rsp = None
        self.error = None


    def _add_content_md5(self):
        self.params.append(("ContentMD5Value", self.content_md5))


    def _cal_content_md5(self):
        m = hashlib.md5()
        m.update(bytes(self.body, "utf-8"))
        self.content_md5 = base64.b64encode(m.digest())


    def _add_sign(self):
        sorted_params = sorted(self.params)
        string_to_sign = "\n".join([self._get_http_method(), self._get_host(), self._get_api_path(), urlencode(sorted_params)])
        self.sign = self._signature(string_to_sign)
        self.params.append(("Signature", self.sign))

    def _request(self):
        self.url = "https://" + self._get_host() + self._get_api_path() + "?" + urlencode(self.params)
        logger.debug("Send wms request, url: %s", self.url)

        try:
            conn = HTTPSConnection(self._get_host(), timeout=self.TIMEOUT)
            conn.request(method=self._get_http_method(), url=self.url, headers=self._get_headers(), body=self.body)
            self.raw_rsp = conn.getresponse().read()
            conn.close()
        except socket.timeout:
            self.error = ('request_timeout', '')
            return False
        logger.debug("Recv wms response, rsp: %s", self.raw_rsp)
        return True

    def _get_headers(self):
        headers = {
            "X-Amazon-User-Agent": "TestApp/1.0(Language=Python)",
            "Content-Type": "text/xml; charset=UTF-8",
        }
        # if self.content_md5 != None:
        #     headers.update({"Content-MD5": self.content_md5})
        return headers

    def _get_secret_key(self):
        return self.seller.secret_key

    def _get_http_method(self):
        return "POST"

    def _get_host(self):
        return self.seller.mws_url.split("//")[1]

    def _get_api_path(self):
        for (section, value) in self.API_SECTIONS.items():
            if self.action in value['Operations']:
                return value['Path']
        assert False

    def _get_api_version(self):
        for (section, value) in self.API_SECTIONS.items():
            if self.action in value['Operations']:
                return value['Version']
        assert False

    def _signature(self, string_to_sign):
        message = bytes(string_to_sign, 'utf-8')
        secret = bytes(self._get_secret_key(), 'utf-8')
        return base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())

    def _gen_common_params(self):
        self.common_params = [
            ("SellerId", self.seller_id),  # send by client
            # "MWSAuthToken": "", # 表示亚马逊卖家对某个开发商的授权。仅适用于网页应用和第三方开发商授权
            ("AWSAccessKeyId", self.aws_access_key_id), # send by client
            ("Action", self.action),
            ("SignatureMethod", self.signature_method),
            ("SignatureVersion", self.signature_version),  # 使用的签名版本。
            ("Timestamp", datetime.now(timezone.utc).replace(microsecond=0).isoformat()),
            ("Version", self.version)
        ]


