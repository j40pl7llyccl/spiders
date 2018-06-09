# -*- coding:utf8 -*-
{
    # 数据抓取的页面URL
    "page_url": "https://haimai.amazon.cn/sales-report?marketplaceId=A1F83G8C2ARO7P",
    # 卖家相关信息
    "seller": {
        "seller_id": "A3SP8O6T2UUODY",
        "access_key": "AKIAIXU22G6SSOCF2WMA",
        "secret_key": "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",
        "mws_url": "https://mws-eu.amazonservices.com",
        "market_place_id": "A1F83G8C2ARO7P",
    },
    # 用户的chrome数据路径
    "chrome_path": r'user-data-dir=C:\Users\pc\AppData\Local\Google\Chrome\User Data',
    # 轮询时间间隔, 单位：秒
    "interval": 60,
    # 商品信息设置
    "items": [
        # 当编号为asin的商品销量小于打折销量时，商品价格为打折单价，
        # 销量大于等于打折销量时，商品价格为原单价
        # 每天在reset_time时将列表中商品单价重置为打折单价
        # (ASIN, 打折销量, 打折时的售价, 打折时的原单价, 不打折时的售价, 不打折时的原单价)
        # ('B076D86JDG', 0, 13.00, 21.00, 12.99, 20.99),
        ('B076D86JDG', 0, 12.99, 20.99, 13.00, 21.00),

        # ('B076D9GC6K', 0, 11.00, 23.00, 10.99, 22.99),
    ]
}
