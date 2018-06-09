import sys, time, logging
from datetime import datetime, timedelta

from tmpl import template

sys.path.append("./")

from lxml import html
import log
from selenium import webdriver
from wms import WMSClient
from jinja2 import Template
from test_data import ppp

logger = logging.getLogger(__name__)

class Browser:
    def __init__(self):
        self.browser = None
        self.page_url = None
        self.login_prompt = ["登录"]

    def init(self, ctx):
        logger.info("启动浏览器 ...")
        options = webdriver.ChromeOptions()
        options.add_argument(ctx.chrome_path)

        self.browser = webdriver.Chrome(chrome_options=options)
        self.browser.set_page_load_timeout(60)
        self.page_url = ctx.page_url

    def login(self):
        self.browser.find_element_by_id("signInSubmit-input").click()
        self.browser.get(self.page_url)
        return not self.is_login_page(self.browser.title)

    def is_login_page(self, title):
        return any([s in title for s in self.login_prompt])

    def goto_page(self):
        logger.info("刷新商品页面 ...")
        self.browser.get(self.page_url)
        if self.is_login_page(self.browser.title):
            logger.info("账号凭证失效，重新登陆中")
            if not self.login():
                logger.error("登陆失败，请检查浏览器账号是否正确")
                sys.exit()
            logger.info("登陆成功，进入商品页面")

    def parse_page(self, page_source=None):
        if page_source == None:
            page_source = self.browser.page_source
        logger.info("解析页面 ...")
        page = html.fromstring(page_source)
        rows = page.xpath('/html/body/section'
                          '/div[2]/div[3]/div[2]'
                          '/table/tbody'
                          '/tr[@class="sales-report-asin-tr"]')
        items = {}
        for idx, row in enumerate(rows, 1):
            if idx == len(rows): break
            [asin] = row.xpath('./td[@field="asin"]/a/text()')
            items[asin] = {}
            [items[asin]["sku"]] = row.xpath('./td[@field="sku"]/text()')
            [items[asin]["count"]] = row.xpath('./td[@field="unitsOrderedToday"]/text()')
        [page_now] = page.xpath('/html/body/section/div[2]/div[3]/div[1]/div/div[1]/div/span[2]/text()')
        page_now = datetime.strptime(page_now.strip(" \n"), "%Y/%m/%d %H:%M:%S")
        logger.info("共%d条商品记录，当前页面时间：%s", len(items), page_now.strftime("%Y/%m/%d %H:%M:%S"))
        logger.debug(items)
        return page_now, items

class Item:
    def __init__(self, asin, count, dis_standard_price, dis_sale_price, ori_standard_price, ori_sale_price, ):
        self.asin = asin
        self.sku = None
        self.count_boundary = count
        self.dis_standard_price = dis_standard_price
        self.dis_sale_price = dis_sale_price
        self.ori_standard_price = ori_standard_price
        self.ori_sale_price = ori_sale_price

        # modify context
        self.count_record = None
        self.last_modify_count = None
        self.modify_standard_price = None
        self.modify_sale_price = None
        self.need_modify_flag = None

    def need_modify_price(self, current_count):
        # if count > count_boundary, set ori
        # if count <= count_boundary, set dis
        if self.last_modify_count == None: return True
        if ((self.last_modify_count > self.count_boundary) and (current_count > self.count_boundary)) or \
            ((self.last_modify_count <= self.count_boundary) and (current_count <= self.count_boundary)):
            return False
        else:
            return True

    def set_need_modify(self, sku, current_count):
        logger.debug("last_modify_count<%s>, current_count<%s>, count_boundary<%s>",
                     self.last_modify_count, current_count, self.count_boundary)
        if self.last_modify_count == None:
            self.last_modify_count = self.count_boundary
        if current_count > self.last_modify_count:
            self.modify_standard_price = self.ori_standard_price
            self.modify_sale_price = self.ori_sale_price
        else:
            self.modify_standard_price = self.dis_standard_price
            self.modify_sale_price = self.dis_sale_price
        self.need_modify_flag = True
        self.count_record = current_count
        self.sku = sku

    def set_modify_succ(self):
        self.last_modify_count = self.count_record
        self.count_record = None
        self.modify_standard_price = None
        self.modify_sale_price = None
        self.need_modify_flag = None


class Seller:
    def __init__(self, seller_id, access_key, secret_key, mws_url, market_place_id):
        self.seller_id = seller_id
        self.access_key = access_key
        self.secret_key = secret_key
        self.mws_url = mws_url
        self.market_place_id = market_place_id

class Context:
    def __init__(self):
        self.config = None
        self.seller = None
        self.items = None
        self.client = None

        self.page_url = None
        self.interval = None
        self.chrome_path = None

    def init(self):
        self.load_config()
        self.init_seller()
        self.init_items()
        self.init_wms_client()
        self.interval = self.config["interval"]
        self.page_url = self.config["page_url"]
        self.chrome_path = self.config["chrome_path"]

    def load_config(self):
        logger.info("初始化配置 ...")
        with open("config.py", "r", encoding="utf8") as file:
            self.config = eval(file.read())
        logger.debug("Config: %s", self.config)

    def init_wms_client(self):
        self.client = WMSClient()
        self.client.set_seller(self.seller)

    def init_seller(self):
        self.seller = Seller(seller_id=self.config["seller"]["seller_id"],
                                access_key=self.config["seller"]["access_key"],
                                secret_key=self.config["seller"]["secret_key"],
                                mws_url=self.config["seller"]["mws_url"],
                                market_place_id=self.config["seller"]["market_place_id"])

    def init_items(self):
        self.items = []
        for (asin, count, dis_sale_price, dis_standard_price, ori_sale_price, ori_standard_price) in self.config["items"]:
            item = Item(asin=asin, count=count,
                        dis_standard_price=dis_standard_price, dis_sale_price=dis_sale_price,
                        ori_standard_price=ori_standard_price, ori_sale_price=ori_sale_price)
            self.items.append(item)

def mark_need_modify_price_items(ctx, page_items):
    logger.info("获取需要设置商品价格的商品 ...")
    items = []
    for item in ctx.items:
        item.need_modify_flag = False
        page_item = page_items.get(item.asin)
        if page_item is None:
            logger.warning("在网页中未找到asin为%s的商品", item.asin)
            continue
        if not item.need_modify_price(int(page_item["count"])): continue
        item.set_need_modify(page_item["sku"], int(page_item["count"]))
        items.append(item)

    if len(items) == 0:
        logger.info("未检测到需要设置商品价格的商品")
    else:
        logger.info("共%d个商品需要设置商品价格", len(items))
        for idx, item in enumerate(items, start=1):
            logger.info("商品<%d>: (asin<%s>, sku<%s>, 标准价格<%s>, 促销价格<%s>, 上次修改数量<%s>, 本次修改数量<%s>, 数量边界<%s>)",
                         idx, item.asin, item.sku, item.modify_standard_price, item.modify_sale_price, item.last_modify_count, item.count_record, item.count_boundary)
    return items

def modify_items_price(ctx, items) -> bool:
    logger.info("提交修改商品价格表单 ...")
    body = template.render(items=items, seller_id=ctx.seller.seller_id,
                           start_date=(datetime.utcnow() - timedelta(days=2)).isoformat(),
                           end_date=(datetime.utcnow() + timedelta(days=30)).isoformat())
    logger.debug(body)
    ok = ctx.client.send_request("SubmitFeed",
                                 [("FeedType", "_POST_PRODUCT_PRICING_DATA_"),
                                  ("MarketplaceIdList.Id.1", ctx.seller.market_place_id)], body=body, max_retry=3)
    if not ok:
        logger.error("Action SubmitFeed failed, reason: send request failed")
        logger.error("修改商品价格失败，原因：提交表单失败")
        return False
    ok = ctx.client.parse_xml_response()
    if not ok:
        logger.error("Action SubmitFeed failed, reason: parse response failed")
        logger.error("修改商品价格失败，原因：提交表单返回错误")
        logger.error(ctx.client.raw_rsp)
        return False

    fid = ctx.client.rsp.SubmitFeedResult[0].FeedSubmissionInfo[0].FeedSubmissionId.text

    time.sleep(5)
    logger.info("获取表单提交结果 ...")
    max_retry_time = 8
    retry_time = 0
    while retry_time < max_retry_time:
        retry_time += 1
        logger.info("第%d次获取表单处理状态 ...", retry_time)
        ok = ctx.client.send_request("GetFeedSubmissionList", [("FeedSubmissionIdList.Id.1", fid)], max_retry=1)
        if not ok:
            logger.warning("GetFeedSubmissionList请求发送失败，等待下次请求")
            time.sleep(45)
            continue

        ok = ctx.client.parse_xml_response()
        if not ok:
            logger.warning("GetFeedSubmissionList解析失败，等待下次请求")
            time.sleep(45)
            continue

        status = ctx.client.rsp.GetFeedSubmissionListResult[0].FeedSubmissionInfo[0].FeedProcessingStatus.text
        logger.info("表单状态: %s", status)
        if status == '_DONE_': break
        if status in ['_IN_PROGRESS_', '_UNCONFIRMED_', '_SUBMITTED_']: pass
        if status == '_CANCELLED_':
            logger.error("修改商品价格失败，原因：表单状态错误")
            return False
        if status in ['_AWAITING_ASYNCHRONOUS_REPLY_', '_IN_SAFETY_NET_']:
            logger.warning("异常的表单状态，status: %s", status)
        logger.info("表单尚未处理完成，等待下一次结果获取")
        time.sleep(45)

    if retry_time >= max_retry_time:
        logger.error("修改商品价格失败，原因：超过最大获取表单状态次数(%s)", retry_time)
        return False

    logger.info("验证表单是否完成")
    ok = ctx.client.send_request("GetFeedSubmissionResult", [("FeedSubmissionId", fid)], max_retry=3)
    if not ok:
        logger.error("修改商品价格失败，原因：获取表单提交结果失败")
        return False
    ok = ctx.client.parse_xml_response()
    if not ok:
        logger.error("修改商品价格失败，原因：获取表单提交结果返回异常")
        return False
    logger.info("表单已经完成，检测是否改价成功")
    msg_cnt = len(items)
    real_cnt = int(ctx.client.rsp.Message[0].ProcessingReport[0].ProcessingSummary[0].MessagesSuccessful.text)
    if real_cnt == msg_cnt:
        logger.info("设置商品价格成功")
        for item in items: item.set_modify_succ()
        return True
    else:
        logger.error("设置商品价格失败，设置商品价格成功数量: %d，失败数量: %d", real_cnt, msg_cnt)
        logger.error(ctx.client.raw_rsp)
        return False

def run():
    ctx = Context()
    ctx.init()
    browser = Browser()
    browser.init(ctx)
    logger.info("开始循环 ...")
    while True:
        logger.info("================================================")
        start = datetime.now()
        browser.goto_page()
        page_now, page_items = browser.parse_page()

        items = mark_need_modify_price_items(ctx, page_items)
        if len(items) != 0:
            modify_items_price(ctx, items)

        end = datetime.now()
        delta = int((end - start).total_seconds())
        sleep = max(ctx.interval - delta, 1)
        logger.info("本次循环用时：%s秒，等待下次检查页面，等待时间：%s秒", delta, sleep)
        time.sleep(sleep)


if __name__ == '__main__':
    run()