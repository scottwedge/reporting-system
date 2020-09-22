# from reporting_api.extensions import db
#
# from reporting_api.models import BaseModel
#
#
# class SalesAnalysisReportModel(BaseModel):
#     __tabl    ename__ = 'view_report_order_dailysale'
#     ord_pay_time = db.Column(db.TIMESTAMP, nullable=True)
#     ord_weekday = db.Column(db.Float)  # 周几
#     pro_sec_type = db.Column(db.Float, nullable=True)  # 二级品类
#     ord_sale_amount = db.Column(db.Float, nullable=True)  # 金额
#     ord_maoli = db.Column(db.Float, nullable=True)  # 毛利
#
#     ord_create_time = db.Column(db.TIMESTAMP, nullable=True)  # 创建日期
#     ord_delivery_time = db.Column(db.TIMESTAMP, nullable=True)  # 发货日期
#     ord_salenum = db.Column(db.Integer, nullable=True)  # 销售数
#     ord_maoli = db.Column(db.Float, nullable=True)  # 毛利
#     ord_sale_amount = db.Column(db.Float, nullable=True)  # 金额
#     ord_weekday = db.Column(db.Float)  # 周几
#     ord_platfee = db.Column(db.Float, nullable=True)  # 平台费
#     ord_expfee = db.Column(db.Float, nullable=True)  # 快递费
#     ord_costfee = db.Column(db.Float, nullable=True)  # 成本费=fob仓对应的值
#     total_adfee = db.Column(db.Float, nullable=True)
#
#     delivery_store = db.Column(db.Float, nullable=True)  # 发货仓
#     ord_province = db.Column(db.Float, nullable=True)  # 省州
#     ord_recordno = db.Column(db.Float, nullable=True)  # 记录号
#     ord_order_code = db.Column(db.Float, nullable=True)  # 订单号
#     ord_country = db.Column(db.Float, nullable=True)  # 国家缩写
#     ord_sitecode = db.Column(db.Float, nullable=True)  # 站点
#     ord_sale_price = db.Column(db.Float, nullable=True)  # 售价
#     ord_costfee = db.Column(db.Float, nullable=True)  # 成本费=fob仓对应的值
#     ord_platfee = db.Column(db.Float, nullable=True)  # 平台费
#     ord_factoryfee = db.Column(db.Float, nullable=True)  # 出厂费
#     ord_fobfee = db.Column(db.Float, nullable=True)  # fob费
#     ord_huanhui = db.Column(db.Float, nullable=True)  # 换回=出厂价/fob
#     pro_materialrate = db.Column(db.Float, nullable=True)  # 材料率
#     ord_pgrossfee = db.Column(db.Float, nullable=True)  # 单位重量的金额
#     ord_volumefee = db.Column(db.Float, nullable=True)  # 单位体积的金额
#     source_code = db.Column(db.VARCHAR, nullable=True)  # 店铺
