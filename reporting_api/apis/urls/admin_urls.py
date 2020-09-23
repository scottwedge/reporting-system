from .. import admin
from ..sales import sales_analysis_report, today_sales, sales_analysis_report_line, test, month_salelog_list, \
    day_sales, third_tier_sale_log, monthly_sales_data, product_type_store_sale_compare, ergonomics_sale_log, \
    global_sale_log, national_sales_analysis, entry_source_fee, global_sale_type_lost_log

urls = [
    # '/', admin.AdminIndex,
    '/reporting/admin/register', admin.Register,
    '/reporting/admin/login', admin.AdminLogin,
    '/reporting/admin/token ', admin.RefreshToken,
    '/reporting/sales/report_order/list', sales_analysis_report.IndependentStationNationalSalesAnalysis,
    '/reporting/sales/report_order/line', sales_analysis_report_line.IndependentStationNationalSalesAnalysisPhoto,
    '/reporting/sales/report_order/today', today_sales.TodaySales,
    '/reporting/sales/report_order/monthlist', month_salelog_list.MonthSalelogList,
    '/reporting/sales/report_order/YearOnYearBasis', month_salelog_list.YearOnYearBasis,
    '/reporting/sales/report_order/MonthOnMonthRatio', month_salelog_list.MonthOnMonthRatio,
    '/reporting/sales/report_order/ThirdTierSaleLog', third_tier_sale_log.ThirdTierSaleLog,
    '/reporting/sales/report_order/MonthlySalesData', monthly_sales_data.MonthlySalesData,
    '/reporting/sales/report_order/ErgonomicsSaleLog', ergonomics_sale_log.ErgonomicsSaleLog,
    '/reporting/sales/report_order/EntrySourceFee', entry_source_fee.EntrySourceFee,
    '/reporting/sales/report_order/GlobalSaleLog', global_sale_log.GlobalSaleLog,
    '/reporting/sales/report_order/ProductTypeStoreSaleCompare',
    product_type_store_sale_compare.ProductTypeStoreSaleCompare,
    '/reporting/sales/report_order/day', day_sales.DaySales,
    '/reporting/sales/report_order/NationalSalesAnalysis', national_sales_analysis.NationalSalesAnalysis,
    '/reporting/sales/report_order/GlobalTyprSaleLostLog', global_sale_type_lost_log.GlobalTyprSaleLostLog,
    '/reporting/sales/report_order/GlobalTyprSaleMiddleLog', global_sale_type_lost_log.GlobalTyprSaleMiddleLog,
    '/test', test.ReportOderList,
]
