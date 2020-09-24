from reporting_api.extensions import db

from reporting_api.models import BaseModel


class SalesAnalysisReportModel(BaseModel):
    __tablename__ = 'report_order'
    ord_pay_time = db.Column(db.TIMESTAMP)
    # ord_create_time = db.Column(db.TIMESTAMP)  # 创建日期
    # ord_delivery_time = db.Column(db.TIMESTAMP)  # 发货日期
    ord_salenum = db.Column(db.Integer)  # 销售数
    ord_maoli = db.Column(db.Float)  # 毛利
    ord_sale_amount = db.Column(db.Float)  # 金额
    # ord_weekday = db.Column(db.VARCHAR)  # 周几
    pro_sec_type = db.Column(db.VARCHAR)  # 二级品类
    # delivery_store = db.Column(db.VARCHAR)  # 发货仓
    # ord_province = db.Column(db.VARCHAR)  # 省州
    # ord_recordno = db.Column(db.VARCHAR)  # 记录号
    # ord_order_code = db.Column(db.VARCHAR)  # 订单号
    ord_country = db.Column(db.VARCHAR)  # 国家缩写
    ord_sitecode = db.Column(db.VARCHAR)  # 站点
    # ord_sale_price = db.Column(db.Float)  # 售价
    ord_expfee = db.Column(db.Float)  # 快递费
    ord_costfee = db.Column(db.Float)  # 成本费=fob仓对应的值
    ord_platfee = db.Column(db.Float)  # 平台费
    ord_factoryfee = db.Column(db.Float)  # 出厂费
    ord_fobfee = db.Column(db.Float)  # fob费
    ord_huanhui = db.Column(db.Float)  # 换回=出厂价/fob
    pro_materialrate = db.Column(db.Float)  # 材料率
    ord_pgrossfee = db.Column(db.Float)  # 单位重量的金额
    ord_volumefee = db.Column(db.Float)  # 单位体积的金额
    source_code = db.Column(db.VARCHAR)  # 店铺
    yyyymm = db.Column(db.VARCHAR)
    pro_pgross = db.Column(db.Float)
    pro_volume = db.Column(db.Float)
    pro_fname = db.Column(db.VARCHAR)  # FOB
    pro_bsname = db.Column(db.VARCHAR)  # 成本费=fob仓对应的值


class ProProductModel(BaseModel):
    __tablename__ = 'pro_product'
    bsname = db.Column(db.VARCHAR)  # 公司型号
    pro_image_path = db.Column(db.VARCHAR)  # 图片地址URL


class OrdSourceAdfeeModel(BaseModel):
    __tablename__ = 'ord_source_ad_fee'
    order_pay_time = db.Column(db.TIMESTAMP)
    week = db.Column(db.VARCHAR)  # 周
    ad_fee_pro_type = db.Column(db.VARCHAR)  # 广告费对应的品类,填二级类的code
    total_ad_fee = db.Column(db.VARCHAR)  # 当日总广告费
    total_us_fee = db.Column(db.VARCHAR)  # 当日美国总广告费
    total_japan_fee = db.Column(db.VARCHAR)  # 当日日本总广告费
    total_europe_fee = db.Column(db.VARCHAR)  # 当日欧洲总广告费
    total_canada_fee = db.Column(db.VARCHAR)  # 当日加拿大总广告费
    total_loctek_fee = db.Column(db.VARCHAR)  # 当日独立站总广告费
    total_google_fee = db.Column(db.VARCHAR)  # 当日谷歌总广告费
    total_india_fee = db.Column(db.VARCHAR)  # 当日印度总广告费
