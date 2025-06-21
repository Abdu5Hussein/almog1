from apscheduler.schedulers.background import BackgroundScheduler
from almogOil import models as almogOil_models
from .whatsapp_service import send_whatsapp_message_via_green_api,send_excel_file_greenapi_upload
from django.utils import timezone
import pandas as pd
from io import BytesIO
from num2words import num2words
import xlsxwriter
from decimal import Decimal

def check_unsent_messages():
    print("[🔄 Scheduler] Checking unsent WhatsApp messages...")

    unsent = almogOil_models.OrderBuyinvoicetable.objects.filter(send=False, source_obj__isnull=False)
    print(f"[📝 Scheduler] Found {unsent.count()} unsent invoices.")

    for record in unsent:
        try:
            # Skip if no phone number
            if not hasattr(record, 'source_obj') or not record.source_obj:
                print(f"[⚠️ Scheduler] Invoice {getattr(record, 'invoice_no', 'UNKNOWN')} skipped: no source object.")
                continue
                
            phone = getattr(record.source_obj, 'phone', '')
            if not phone:
                print(f"[⚠️ Scheduler] Invoice {getattr(record, 'invoice_no', 'UNKNOWN')} skipped: no phone number.")
                continue

            items = almogOil_models.OrderBuyInvoiceItemsTable.objects.filter(invoice_no=record)
            if not items.exists():
                print(f"[⚠️ Scheduler] No items found for invoice {getattr(record, 'invoice_no', 'UNKNOWN')}.")
                continue

            # Get date from available fields or use current date
            invoice_date = ""
            if hasattr(record, 'date') and record.date:
                invoice_date = record.date.strftime('%Y.%m.%d')
            elif hasattr(record, 'created_at') and record.created_at:
                invoice_date = record.created_at.strftime('%Y.%m.%d')
            elif hasattr(record, 'invoice_date') and record.invoice_date:
                invoice_date = record.invoice_date.strftime('%Y.%m.%d')
            else:
                invoice_date = timezone.now().strftime('%Y.%m.%d')

            # Get the total amount from OrderBuyinvoicetable
            total_amount = float(getattr(record, 'amount', 0))
            total = float(getattr(record, 'buy_net_amount', 0))
            # Prepare Arabic invoice data
            invoice_data = {
                'company_name': 'شركة مارين لاستيراد قطع غيار السيارات و زيوتها',
                'invoice_no': getattr(record, 'invoice_no', ''),
                'date': invoice_date,
                'payment_type': getattr(record, 'payment_type', 'آجلة'),
                'customer_name': getattr(record.source_obj, 'name', ''),
                'customer_info': getattr(record.source_obj, 'address', ''),
                'items': [],
                'hoz_total': total,
                'commission':  getattr(record.source_obj, 'commission', ''),  # Assuming no commission in this case
                'total': total_amount,
                'total_in_words': '',
                'notes': [
                     '💻 زر موقعنا الإلكتروني الآن واستمتع بالعروض الحصرية: [www.hozma.com]',
                     '📞 لمزيد من التفاصيل، يمكنك الاتصال بنا على الرقم: 123-456-7890.'
                     'فاتورة اصدرت تلقائيا من نظام حزمة',

                ]
            }

            # Convert total to Arabic words with Libyan Dinar
            try:
                invoice_data['total_in_words'] = num2words(invoice_data['total'], lang='ar') + ' دينار ليبي فقط لا غير'
            except:
                invoice_data['total_in_words'] = f"المبلغ الإجمالي: {invoice_data['total']} دينار ليبي"

            # Fetch items
            for item in items:
                invoice_data['items'].append({
                    'pno': getattr(item, 'pno', ''),
                    'name': getattr(item, 'name', ''),
                    'company': getattr(item, 'company', ''),
                    'Asked_quantity': getattr(item, 'Asked_quantity', 0),
                    'Confirmed_quantity': getattr(item, 'Confirmed_quantity', 0),
                    'dinar_unit_price': getattr(item, 'dinar_unit_price', 0),
                    'main_cat': getattr(item, 'main_cat', ''),
                    'sub_cat': getattr(item, 'sub_cat', '')
                })

            # Create Excel file with the exact styling from create_excel_invoice
            excel_buffer = BytesIO()
            workbook = xlsxwriter.Workbook(excel_buffer)
            worksheet = workbook.add_worksheet('فاتورة')

            # Page setup for A4
            worksheet.set_paper(9)  # A4 paper
            worksheet.set_portrait()
            worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
            worksheet.set_print_scale(90)
            worksheet.hide_gridlines(2)
            worksheet.fit_to_pages(1, 1)

            rtl_format = {'reading_order': 2}

            # Company Name - Larger, bold, and center-aligned with bottom border
            company_format = workbook.add_format({
                **rtl_format,
                'bold': True,
                'font_size': 18,
                'align': 'center',
                'valign': 'vcenter',
                'font_name': 'Arial',
                'bottom': 3,
                'font_color': '#003366'
            })

            # Invoice header info format - bold, medium size, right-aligned
            header_label_format = workbook.add_format({
                **rtl_format,
                'bold': True,
                'font_size': 12,
                'align': 'right',
                'font_name': 'Arial',
                'valign': 'vcenter'
            })

            header_value_format = workbook.add_format({
                **rtl_format,
                'font_size': 12,
                'align': 'right',
                'font_name': 'Arial',
                'valign': 'vcenter'
            })

            # Address and customer info format
            customer_info_format = workbook.add_format({
                **rtl_format,
                'font_size': 11,
                'align': 'right',
                'font_name': 'Arial',
                'text_wrap': True,
                'valign': 'top'
            })

            # Table header format - bold with background and border
            table_header_format = workbook.add_format({
                **rtl_format,
                'bold': True,
                'font_size': 12,
                'bg_color': '#4F81BD',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'font_name': 'Arial',
                'text_wrap': True
            })

            # Item cell format (Right aligned)
            item_cell_right = workbook.add_format({
                **rtl_format,
                'font_size': 11,
                'border': 1,
                'align': 'right',
                'valign': 'vcenter',
                'font_name': 'Arial',
                'text_wrap': True
            })

            # Item name format - larger, bold, right aligned
            item_name_format = workbook.add_format({
                **rtl_format,
                'bold': True,
                'font_size': 13,
                'border': 1,
                'align': 'right',
                'valign': 'vcenter',
                'font_name': 'Arial',
                'text_wrap': True,
                'font_color': '#2F5496'
            })

            # Currency format (Right aligned)
            currency_format = workbook.add_format({
                **rtl_format,
                'font_size': 11,
                'border': 1,
                'align': 'right',
                'num_format': '#,##0.00 "د.ل"',
                'font_name': 'Arial'
            })

            # Total row format - bold, larger font, right aligned with border
            total_format = workbook.add_format({
                **rtl_format,
                'bold': True,
                'font_size': 13,
                'border': 1,
                'align': 'right',
                'font_name': 'Arial',
                'font_color': '#000000'
            })

            # Total amount value format - bold, larger font, center aligned
            total_value_format = workbook.add_format({
                **rtl_format,
                'bold': True,
                'font_size': 13,
                'border': 1,
                'align': 'center',
                'font_name': 'Arial',
                'num_format': '#,##0.00 "د.ل"',
                'font_color': '#000000'
            })

            # Amount in words format - italic, right aligned
            amount_words_format = workbook.add_format({
                **rtl_format,
                'italic': True,
                'font_size': 11,
                'align': 'right',
                'font_name': 'Arial',
                'text_wrap': True,
                'font_color': '#666666'
            })

            # Notes format
            notes_format = workbook.add_format({
                **rtl_format,
                'font_size': 11,
                'align': 'right',
                'font_name': 'Arial',
                'text_wrap': True,
                'valign': 'top'
            })

            # Signature format
            signature_format = workbook.add_format({
                **rtl_format,
                'bold': True,
                'font_size': 12,
                'align': 'center',
                'font_name': 'Arial',
                'bottom': 1
            })

            # Write Company Name (Merged across B-G to center it better)
            worksheet.merge_range('B1:G1', invoice_data['company_name'], company_format)
            worksheet.set_row(0, 30)

            # Invoice details - shifted one column to the right (B instead of A)
            worksheet.merge_range('B2:C2', f'فاتورة شراء رقم:{invoice_data["invoice_no"]}', header_value_format)
            worksheet.merge_range('E2:F2', f'التاريخ:{invoice_data["date"]}', header_value_format)
            worksheet.merge_range('B3:C3', f'نوع الدفع:{invoice_data["payment_type"]}', header_value_format)
            worksheet.merge_range('E3:F3', f'اسم المورد:{invoice_data["customer_name"]}', header_value_format)
            worksheet.merge_range('E4:G4', f'عنوان المورد:{invoice_data["customer_info"]}', customer_info_format)

            # Spacing rows
            worksheet.set_row(3, 35)
            worksheet.set_row(4, 30)

            # Table headers starting at row 5 (index 5) - shifted one column to the right
            headers = ['السعر', 'الكمية', 'بيان الصنف', 'رقم الصنف']  # Reversed order
            col_widths = [20, 15, 50, 15]

            start_col = 4  # Column E
            for i, (header, width) in enumerate(zip(headers, col_widths)):
                col_idx = start_col - i
                worksheet.write(5, col_idx, header, table_header_format)
                worksheet.set_column(col_idx, col_idx, width)

            # Write items starting at row 6 - shifted one column to the right
            row = 6
            for item in invoice_data['items']:
                worksheet.write(row, 4, item['dinar_unit_price'], currency_format)  # السعر
                worksheet.write(row, 3, item['Asked_quantity'], item_cell_right)    # الكمية
                worksheet.write(row, 2, f"{item['name']} / {item['company'] or ''}", item_name_format)  # بيان الصنف
                worksheet.write(row, 1, item['pno'], item_cell_right)     # column E
                worksheet.set_row(row, 25)
                row += 1

            # Total rows - one under the other, right-aligned
            worksheet.write(row, 4, 'المبلغ الإجمالي:', total_format)
            worksheet.write(row, 3, invoice_data['hoz_total'], total_value_format)
            worksheet.set_row(row, 25)
            row += 1

            worksheet.write(row, 4, 'الخصم:', total_format)
            worksheet.write(row, 3, invoice_data['commission'], total_value_format)
            worksheet.set_row(row, 25)
            row += 1

            worksheet.write(row, 4, 'الصافي:', total_format)
            worksheet.write(row, 3, invoice_data['total'], total_value_format)
            worksheet.set_row(row, 25)
            row += 1

            # Empty row for spacing
            worksheet.set_row(row, 10)
            row += 1

            # Total amount in words - shifted one column to the right
            worksheet.merge_range(row, 1, row, 6, f'المبلغ بالحروف: {invoice_data["total_in_words"]}', amount_words_format)
            worksheet.set_row(row, 25)
            row += 2

            # Notes - shifted one column to the right
            for note in invoice_data['notes']:
                worksheet.merge_range(row, 1, row, 6, note, notes_format)
                worksheet.set_row(row, 20)
                row += 1

            # Signature lines - shifted one column to the right
            row += 2
            worksheet.merge_range(row, 1, row, 3, 'توقيع المورد:', signature_format)  # columns B-D
            worksheet.merge_range(row, 4, row, 6, 'توقيع المستلم:', signature_format)  # columns E-G
            worksheet.set_row(row, 35)

            workbook.close()
            excel_buffer.seek(0)

            file_name = f"invoice_{invoice_data['invoice_no']}.xlsx"
            success = send_excel_file_greenapi_upload(phone, file_name, excel_buffer)

            if success:
                print(f"[✅ Scheduler] Sent invoice {invoice_data['invoice_no']} to {phone}")
                record.send = True
                record.send_date = timezone.now()
                record.save()
            else:
                print(f"[❌ Scheduler] Failed to send invoice {invoice_data['invoice_no']} to {phone}")

        except Exception as e:
            print(f"[🔥 Scheduler] Error processing invoice {getattr(record, 'invoice_no', 'UNKNOWN')}: {str(e)}")
            continue
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_unsent_messages, 'interval', minutes=120)
    scheduler.start()
    print("✅ Scheduler started successfully.")

