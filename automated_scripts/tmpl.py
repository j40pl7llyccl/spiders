from jinja2 import Template

template = Template('''<?xml version="1.0" encoding="utf-8" ?>
<AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
    <Header>
        <DocumentVersion>1.01</DocumentVersion>
        <MerchantIdentifier>{{seller_id}}</MerchantIdentifier>
    </Header>
    <MessageType>Price</MessageType>
    {% for item in items %}
    <Message>
        <MessageID>{{loop.index}}</MessageID>
        <Price>
            <SKU>{{item.sku}}</SKU>
            <StandardPrice currency="GBP">{{item.modify_standard_price}}</StandardPrice>
            <Sale>
                <StartDate>{{start_date}}</StartDate>
                <EndDate>{{end_date}}</EndDate>
                <SalePrice currency="GBP">{{item.modify_sale_price}}</SalePrice> 
            </Sale>
        </Price>
    </Message>
    {% endfor %}
</AmazonEnvelope>
''')