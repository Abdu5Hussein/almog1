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
            
            # Prepare Arabic invoice data
            invoice_data = {
                'company_name': 'شركة مارين لاستيراد قطع غيار السيارات و زيوتها',
                'invoice_no': getattr(record, 'invoice_no', ''),
                'date': invoice_date,
                'payment_type': getattr(record, 'payment_type', 'آجلة'),
                'customer_name': getattr(record.source_obj, 'name', ''),
                'customer_info': getattr(record.source_obj, 'address', ''),
                'items': [],
                'total': total_amount,
                'total_in_words': '',
                'notes': [
                    'لا يتم ترجيح أي اصناف بالفاتورة بخصوص السعر',
                    'يجب استلام البضاعة خلال 3 أيام من تاريخ الفاتورة'
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

            # Create Excel file with Arabic formatting
            excel_buffer = BytesIO()
            workbook = xlsxwriter.Workbook(excel_buffer)
            worksheet = workbook.add_worksheet('فاتورة')
            
            # Arabic formatting styles
            arabic_header_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'align': 'center',
                'valign': 'vcenter',
                'font_name': 'Arial'  # Use a font that supports Arabic
            })
            
            arabic_company_format = workbook.add_format({
                'bold': True,
                'font_size': 18,
                'align': 'center',
                'valign': 'vcenter',
                'font_name': 'Arial'
            })
            
            arabic_info_format = workbook.add_format({
                'font_size': 14,
                'align': 'right',
                'font_name': 'Arial'
            })
            
            arabic_table_header_format = workbook.add_format({
                'bold': True,
                'font_size': 12,
                'bg_color': '#DDDDDD',
                'border': 1,
                'align': 'center',
                'font_name': 'Arial'
            })
            
            arabic_cell_format = workbook.add_format({
                'font_size': 12,
                'border': 1,
                'align': 'center',
                'font_name': 'Arial'
            })
            
            arabic_right_align_format = workbook.add_format({
                'font_size': 12,
                'border': 1,
                'align': 'right',
                'font_name': 'Arial'
            })
            
            arabic_currency_format = workbook.add_format({
                'font_size': 12,
                'border': 1,
                'align': 'center',
                'num_format': '#,##0.00 "د.ل"',
                'font_name': 'Arial'
            })
            
            # Write company header (bigger font)
            worksheet.merge_range('A1:F1', invoice_data['company_name'], arabic_company_format)
            
            # Write invoice info (bigger cells for invoice number)
            worksheet.merge_range('A3:B3', f'فاتورة شراء رقم : {invoice_data["invoice_no"]}', arabic_info_format)
            worksheet.write('C3', f'التاريخ : {invoice_data["date"]}', arabic_info_format)
            worksheet.write('D3', invoice_data['payment_type'], arabic_info_format)
            
            # Write customer info (bigger cells for customer name)
            worksheet.merge_range('A4:B4', f'اسم المورد : {invoice_data["customer_name"]}', arabic_info_format)
            worksheet.write('C4', invoice_data['customer_info'], arabic_info_format)
            
            # Write table headers
            headers = ['رقم الصنف', 'بيان الصنف', 'الكمية المطلوبة', 'الكمية المؤكدة', 'سعر الوحدة', 'التصنيف']
            for col, header in enumerate(headers):
                worksheet.write(5, col, header, arabic_table_header_format)
            
            # Write items
            row = 6
            for item in invoice_data['items']:
                worksheet.write(row, 0, item['pno'], arabic_cell_format)
                worksheet.write(row, 1, f"{item['name']} / {item['company'] if item['company'] else ''}", arabic_right_align_format)
                worksheet.write(row, 2, item['Asked_quantity'], arabic_cell_format)
                worksheet.write(row, 3, item['Confirmed_quantity'] if item['Confirmed_quantity'] else '-', arabic_cell_format)
                worksheet.write(row, 4, item['dinar_unit_price'], arabic_currency_format)
                worksheet.write(row, 5, f"{item['main_cat']} / {item['sub_cat']}", arabic_cell_format)
                row += 1
            
            # Write total amount in Libyan Dinar
            worksheet.write(row, 3, 'المبلغ الإجمالي:', arabic_table_header_format)
            worksheet.write(row, 4, invoice_data['total'], arabic_currency_format)
            row += 2
            
            # Write total in words (Libyan Dinar)
            worksheet.merge_range(f'A{row+1}:F{row+1}', f'فقط {invoice_data["total_in_words"]}', arabic_info_format)
            row += 2
            
            # Write notes
            for note in invoice_data['notes']:
                worksheet.write(row, 0, note, arabic_right_align_format)
                row += 1
            
            # Adjust column widths (larger for Arabic text)
            worksheet.set_column('A:A', 15)  # Wider for item numbers
            worksheet.set_column('B:B', 40)  # Much wider for Arabic descriptions
            worksheet.set_column('C:C', 20)  # Quantity columns wider
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 20)  # Price column
            worksheet.set_column('F:F', 25)  # Category column
            
            workbook.close()
            excel_buffer.seek(0)

            file_name = f"invoice_{invoice_data['invoice_no']}.xlsx"
            success = send_excel_file_greenapi_upload(phone, file_name, excel_buffer)

            if success:
                print(f"[✅ Scheduler] Sent invoice {invoice_data['invoice_no']} to {phone}")
                record.send = True
                record.save()
            else:
                print(f"[❌ Scheduler] Failed to send invoice {invoice_data['invoice_no']} to {phone}")

        except Exception as e:
            print(f"[🔥 Scheduler] Error processing invoice {getattr(record, 'invoice_no', 'UNKNOWN')}: {str(e)}")
            continue
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_unsent_messages, 'interval', minutes=0.5)
    scheduler.start()
    print("✅ Scheduler started successfully.")

