# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class AllClientsTable(models.Model):
    clientid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    address = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    email = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    website = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    phone = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    mobile = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    last_transaction = models.DateField(blank=True, null=True)
    accountcurr = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    type = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    category = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    loan_period = models.IntegerField(blank=True, null=True)
    loan_limit = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    loan_day = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    subtype = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    client_stop = models.BooleanField(blank=True, null=True)
    curr_flag = models.BooleanField(blank=True, null=True)
    fcm_token = models.TextField(null=True, blank=True)
    permissions = models.CharField(max_length=400, db_collation='Arabic_CI_AS', blank=True, null=True)
    other = models.CharField(max_length=400, db_collation='Arabic_CI_AS', blank=True, null=True)
    last_transaction_details = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    last_transaction_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    geo_location = models.CharField(max_length=200, blank=True, null=True)
    # New fields
    username = models.CharField(max_length=150, unique=True,null=True)  # Ensure username is unique
    password = models.CharField(max_length=255,null=True)  # This will store the hashed password

    class Meta:
        managed = True
        db_table = 'All_Clients_Table'

    def set_password(self, raw_password):
        """Hashes the password before saving."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Checks if the given raw password matches the stored hash."""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)


class AllSourcesTable(models.Model):
    clientid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    address = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    email = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    website = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    phone = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    mobile = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    last_transaction_details = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    last_transaction_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    last_transaction = models.DateField(blank=True, null=True)
    accountcurr = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    type = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    category = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    loan_period = models.IntegerField(blank=True, null=True)
    loan_limit = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    loan_day = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    subtype = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    client_stop = models.BooleanField(blank=True, null=True)
    curr_flag = models.BooleanField(blank=True, null=True)
    permissions = models.CharField(max_length=400, db_collation='Arabic_CI_AS', blank=True, null=True)
    other = models.CharField(max_length=400, db_collation='Arabic_CI_AS', blank=True, null=True)
    # New fields
    username = models.CharField(max_length=150, unique=True,null=False)  # Ensure username is unique
    password = models.CharField(max_length=255,null=False)  # This will store the hashed password
    commission = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)



    class Meta:
        managed = True
        db_table = 'All_Sources_Table'

    def set_password(self, raw_password):
        """Hashes the password before saving."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Checks if the given raw password matches the stored hash."""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)


class Blancetable(models.Model):
    fileid = models.IntegerField(db_column='FileId')  # Field name made lowercase.
    itemid = models.IntegerField(db_column='ItemId', blank=True, null=True)  # Field name made lowercase.
    itemno = models.CharField(db_column='ItemNo', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemmain = models.CharField(db_column='ItemMain', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemvalue = models.IntegerField(db_column='ItemValue', blank=True, null=True)  # Field name made lowercase.
    tdate = models.DateTimeField(db_column='TDate', blank=True, null=True)  # Field name made lowercase.
    tname = models.CharField(db_column='TName', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    tno = models.CharField(db_column='TNo', max_length=10, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    tvalue = models.IntegerField(db_column='TValue', blank=True, null=True)  # Field name made lowercase.
    ttype = models.IntegerField(db_column='TType', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'BlanceTable'


class Buyinvoicetable(models.Model):
    autoid = models.AutoField(primary_key=True)
    original_no = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    invoice_date = models.DateTimeField(blank=True, null=True)
    source = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    discount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    expenses = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    net_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    account_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    arrive_date = models.DateField(blank=True, null=True)
    ready_date = models.DateField(blank=True, null=True)
    confirmation_date = models.DateField(blank=True, null=True)
    remind_before = models.IntegerField(blank=True, null=True)
    temp_flag = models.BooleanField(blank=True, null=True)
    order_no = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    multi_source_flag = models.BooleanField(blank=True, null=True)
    currency = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    invoice_no = models.IntegerField(unique=True)
    paid_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    discount_dinar = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    expenses_dinar = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    confirmed = models.BooleanField(default=False)
    send = models.BooleanField(default=False)
    send_date = models.DateTimeField(blank=True, null=True)
    source_obj = models.ForeignKey('AllSourcesTable', on_delete=models.CASCADE, blank=True, null=True)



    class Meta:
        managed = True
        db_table = 'BuyInvoiceTable'

class SellinvoiceTable(models.Model):
    autoid = models.AutoField(primary_key=True)
    invoice_date = models.DateTimeField(blank=True, null=True)
    client_obj= models.ForeignKey(AllClientsTable,on_delete=models.CASCADE)
    client_id = models.CharField(max_length=30, db_collation='Arabic_CI_AS', blank=True, null=True)
    client_name = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    client_rate = models.CharField(max_length=60, blank=True, null=True)
    client_category = models.CharField(max_length=60, blank=True, null=True)
    client_limit = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    client_balance = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    payment_status = models.CharField(max_length=60, blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    discount = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    taxes = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    net_amount = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    returned = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    # return_id = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    paid_amount = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    employee = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    delivered_date = models.DateTimeField(blank=True, null=True)
    deliver_request = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    invoice_status = models.CharField(max_length=60, blank=True, null=True)
    price_status = models.CharField(max_length=60, blank=True, null=True)
    invoice_no = models.IntegerField(unique=True)
    for_who = models.CharField(max_length=100, blank=True, null=True)
    partial_flag = models.BooleanField(default=False)
    notes = models.CharField(max_length=400, blank=True, null=True)
    preparer_name = models.CharField(max_length=100, blank=True, null=True)
    reviewer_name = models.CharField(max_length=100, blank=True, null=True)
    biller_name = models.CharField(max_length=100, blank=True, null=True)
    deliverer_name = models.CharField(max_length=100, blank=True, null=True)
    preparer_note = models.CharField(max_length=1000, blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.IntegerField(default=0)
    delivered_quantity = models.IntegerField(default=0)
    sent_by = models.CharField(max_length=1000, blank=True, null=True)
    office = models.CharField(max_length=1000, blank=True, null=True)
    office_no = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.BooleanField(default=False)
    delivery_status = models.CharField(max_length=150, default="معلقة")
    is_assigned = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice {self.autoid}"

    class Meta:
        managed = True
        db_table = 'SellInvoiceTable'

class Clientstable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    pno_instance = models.ForeignKey('Mainitem', on_delete=models.DO_NOTHING)
    itemno = models.CharField(db_column='itemno', max_length=50, blank=True, null=True)  # Field name made lowercase.
    maintype = models.CharField(db_column='maintype', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='itemname', max_length=200, blank=True, null=True)  # Field name made lowercase.
    currentbalance = models.IntegerField(db_column='currentbalance',  blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='date', blank=True, null=True)
    clientname = models.CharField(db_column='clientname', max_length=25, blank=True, null=True)  # Field name made lowercase.
    billno = models.CharField(db_column='billno', max_length=25, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='description', max_length=25, blank=True, null=True)  # Field name made lowercase.
    clientbalance = models.IntegerField(db_column='clientbalance', blank=True, null=True)  # Field name made lowercase.
    pno = models.CharField(db_column='pno', max_length=50, blank=True, null=True)


    class Meta:
        managed = True
        db_table = 'ClientsTable'


class Companytable(models.Model):
    fileid = models.BigAutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    companyname = models.CharField(db_column='CompanyName', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    logo_obj = models.ImageField(upload_to='logos/', blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'CompanyTable'


class Imagetable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    productid = models.IntegerField(db_column='ProductId', blank=True, null=True)  # Field name made lowercase.
    image = models.CharField(db_column='Image', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    image_obj = models.ImageField(upload_to='product_images/', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ImageTable'


class LostAndDamagedTable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    itemno = models.CharField(db_column='ItemNo', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    companyno = models.CharField(db_column='CompanyNo', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    user = models.CharField(db_column='User', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    quantity = models.IntegerField(db_column='Quantity', blank=True, null=True)  # Field name made lowercase.
    company = models.CharField(db_column='Company', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    costprice = models.DecimalField(db_column='CostPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    pno = models.ForeignKey('Mainitem', models.DO_NOTHING)
    status = models.CharField(db_column='Status', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pno_value = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Lost_and_damaged_Table'


class Mainitem(models.Model):
    fileid = models.BigAutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    itemno = models.CharField(db_column='ItemNo', max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemmain = models.CharField(db_column='ItemMain', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemsubmain = models.CharField(db_column='ItemSubMain', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    short_name = models.CharField(db_column='ShortName', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemthird = models.CharField(db_column='ItemThird', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemsize = models.CharField(db_column='ItemSize', max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    companyproduct = models.CharField(db_column='CompanyProduct', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    dateproduct = models.CharField(db_column='DateProduct', max_length=110, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    levelproduct = models.CharField(db_column='LevelProduct', max_length=110, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemvalue = models.IntegerField(db_column='ItemValue', default=0)  # Field name made lowercase.
    itemtemp = models.IntegerField(db_column='ItemTemp', default=0)  # Field name made lowercase.
    itemplace = models.CharField(db_column='ItemPlace', max_length=110, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orderlastdate = models.DateTimeField(db_column='OrderLastDate', blank=True, null=True)  # Field name made lowercase.
    ordersource = models.CharField(db_column='OrderSource', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orderbillno = models.CharField(db_column='OrderBillNo', max_length=110, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    buylastdate = models.DateTimeField(db_column='buyLastdate', blank=True, null=True)  # Field name made lowercase.
    buysource = models.CharField(db_column='BuySource', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    buybillno = models.CharField(db_column='BuyBillNo', max_length=110, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orgprice = models.DecimalField(db_column='OrgPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    orderprice = models.DecimalField(db_column='OrderPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    costprice = models.DecimalField(db_column='CostPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    buyprice = models.DecimalField(db_column='BuyPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    memo = models.CharField(db_column='Memo', max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orderstop = models.BooleanField(db_column='OrderStop', blank=True, null=True)  # Field name made lowercase.
    buystop = models.BooleanField(db_column='BuyStop', blank=True, null=True)  # Field name made lowercase.
    itemtrans = models.BooleanField(db_column='ItemTrans', blank=True, null=True)  # Field name made lowercase.
    itemvalueb = models.IntegerField(db_column='ItemValueB', blank=True, null=True)  # Field name made lowercase.
    replaceno = models.CharField(db_column='ReplaceNo', max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemtype = models.CharField(db_column='ItemType', max_length=115, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    barcodeno = models.CharField(db_column='BarcodeNo', max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    eitemname = models.CharField(db_column='EItemName', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    currtype = models.CharField(db_column='CurrType', max_length=115, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    lessprice = models.DecimalField(db_column='LessPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    pno = models.IntegerField(db_column='PNo', blank=False, null=False, unique=True)  # Field name made lowercase.
    currvalue = models.DecimalField(db_column='CurrValue', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    resvalue = models.IntegerField(db_column='resValue', blank=True, null=True)  # Field name made lowercase.
    itemperbox = models.IntegerField(db_column='ItemPerbox', blank=True, null=True)  # Field name made lowercase.
    cstate = models.IntegerField(db_column='CSTate', blank=True, null=True)  # Field name made lowercase.
    oem_numbers = models.CharField(max_length=1000, blank=True, null=True)
    engine_no = models.CharField(max_length=300, blank=True, null=True)
    json_description = models.JSONField(null=True,blank=True)
    showed = models.IntegerField(default=0)
    source_pno = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
     # Adding the foreign key to AllSourcesTable is for HOZMA ATTENTIN IS FOR HOZMA
    source = models.ForeignKey('AllSourcesTable', on_delete=models.CASCADE, blank=True, null=True)
    category = models.CharField(db_column='category', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    discount = models.DecimalField(db_column='discount', max_digits=19, decimal_places=4, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'MainItem'
        indexes = [
            models.Index(
                fields=['itemno'],
                name='MainItem_ItemNo_266fc6_idx'
            ),
            models.Index(
                fields=['itemname'],
                name='MainItem_ItemNam_150b8b_idx'
            ),
            models.Index(
                fields=['itemmain'],
                name='MainItem_ItemMai_d36971_idx'
            ),
            models.Index(
                fields=['itemsubmain'],
                name='MainItem_ItemSub_3ccf4b_idx'
            ),
            models.Index(
                fields=['companyproduct'],
                name='MainItem_Company_355d09_idx'
            ),
            # Index with 'itemmain' and additional included columns
            models.Index(
                fields=['itemmain'],
                name='MainItem_partial_with_includes',
                include=[
                    'fileid', 'itemno', 'itemsubmain', 'itemname',
                    'itemthird', 'itemsize', 'companyproduct', 'itemvalue',
                    'itemtemp', 'itemplace', 'buyprice', 'memo', 'replaceno',
                    'barcodeno', 'eitemname', 'currtype', 'lessprice', 'pno',
                    'currvalue', 'itemvalueb', 'costprice', 'resvalue', 'orderprice',
                    'orderlastdate', 'ordersource', 'orderbillno',
                    'buylastdate', 'buysource', 'buybillno', 'orgprice'
                ]
            ),
            models.Index(
                fields=['replaceno'],
                name='MainItem_replaceno_1_idx'
            ),
            models.Index(
                fields=['itemmain', 'itemname'],
                name='itemmain_itemname_idx'
            ),
            models.Index(fields=['itemmain', 'itemname', 'companyproduct'], name='idx_main_name_company'),
        ]


class Oemtable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    cname = models.CharField(db_column='CName', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    cno = models.CharField(db_column='CNo', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    oemno = models.TextField(db_column='OEMNO', db_collation='Arabic_CI_AS', blank=True, null=True)
  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'OEMTable'


class Sectionstable(models.Model):
    autoid = models.AutoField(primary_key=True)
    section = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    description = models.CharField(max_length=300, db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'SectionsTable'

class Subsectionstable(models.Model):
    autoid = models.AutoField(primary_key=True)
    subsection = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    description = models.CharField(max_length=300, db_collation='Arabic_CI_AS', blank=True, null=True)
    sectionid = models.ForeignKey(Sectionstable, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'subSectionsTable'

class StorageTransactionsTable(models.Model):
    storageid = models.AutoField(primary_key=True)
    account_type = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    transaction = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    transaction_date = models.DateField(blank=True, null=True)
    reciept_no = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    place = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    section = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    subsection = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    person = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    issued_for = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    note = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    payment = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    daily_status = models.BooleanField()
    bank = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    check_no = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    done_by = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    print_status = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Storage_Transactions_Table'


class Ttable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    tname = models.CharField(db_column='TName', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'TTable'


class Tablerights(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'TableRights'


class Titletable(models.Model):
    fileid = models.BigAutoField(db_column='Fileid', primary_key=True)  # Field name made lowercase.
    titlename = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'TitleTable'


class BuyinvoiceCosts(models.Model):
    autoid = models.AutoField(primary_key=True)
    cost_for = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    cost_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    dinar_cost_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    invoice = models.ForeignKey(Buyinvoicetable, models.DO_NOTHING)
    invoice_no = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'buyinvoice_costs'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150, db_collation='Arabic_CI_AS')

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255, db_collation='Arabic_CI_AS')
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100, db_collation='Arabic_CI_AS')

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128, db_collation='Arabic_CI_AS')
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150, db_collation='Arabic_CI_AS')
    first_name = models.CharField(max_length=150, db_collation='Arabic_CI_AS')
    last_name = models.CharField(max_length=150, db_collation='Arabic_CI_AS')
    email = models.CharField(max_length=254, db_collation='Arabic_CI_AS')
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'
        permissions = [

            ('category_products', 'قسم الاصناف'),
            ('template_productdetails', 'صفحة بيانات الاصناف'),
            ('template_local_item_reports', 'تقارير الاصناف المحلية'),
            ('template_external_item_reports', 'تقارير الاصناف الخارجية'),
            ('template_price_modifications', 'تعديل الاسعار'),
            ('template_item_movement_reports', 'تقرير حركة الاصناف'),
            ('template_item_revaluation', 'اعادة ترصيد الاصناف'),
            ('template_inventory', 'الجرد'),
            ('template_damage_loss', 'التلف والفقد'),
            ('template_storage_locations', 'اماكن التخزين'),
            ('template_english_labeling', 'التسمية الانجليزية'),
            ('template_item_reservation', 'حجز اصناف'),
            ('template_revaluation', 'اعادة الترصيد'),
            ('template_missing_items', 'النواقص'),
            ('template_issue_permits', 'اذونات الصرف'),
            ('template_items_with_notes', 'اصناف بالملاحظات'),
            ('template_add_item_specifications', 'اضافة مواصفات الصنف'),
            ('export_mainitems', 'تصدير الاصناف'),

            ('category_sell_invoice', 'قسم فواتير البيع'),
            ('template_sell_invoice_entry', 'ادخال فاتورة بيع'),
            ('template_sell_invoices', 'فواتير البيع'),
            ('template_sell_invoice_settlement', 'تسوية حساب فواتير البيع'),
            ('template_sell_inventory_item_search', 'بحث باصناف المخزن'),
            ('template_sell_invoice_preparation_reports', 'تقارير التحضير'),
            ('export_sellinvoice', 'تصدير فواتير البيع'),
            ('custom_export_sellinvoice', 'تصدير مخصص لفواتير البيع'),
            ('show_total_sellinvoice', 'عرض مجاميع فواتير البيع'),
            ('show_items_sellinvoice', 'عرض اصناف فواتير البيع'),
            ('prepare_input_sellinvoice', 'ادخال تحضير فواتير البيع'),
            ('show_sell_price_sellinvoice', 'عرض سعر البيع في فواتير البيع'),
            ('edit_sell_price_sellinvoice', 'تعديل سعر البيع في فواتير البيع'),
            ('edit_quantity_sellinvoice', 'تعديل الكمية في فواتير البيع'),
            ('fixed_date_sellinvoice', 'تثبيت التاريخ في فواتير البيع'),
            ('fixed_date_prepare_sellinvoice', 'تثبيت التاريخ في تقارير التحضير'),

            ('category_buy_invoice', 'قسم فواتير الشراء'),
            ('template_buy_invoice_entry', 'ادخال فاتورة شراء'),
            ('template_buy_invoices', 'فواتير الشراء'),
            ('template_buy_price_modifications', 'تعديل اسعار البيع'),
            ('template_buy_invoice_settlement', 'تسوية حساب فواتير الشراء'),
            ('template_buy_temp_item_posting', 'ترحيل الاصناف المؤقتة'),
            ('template_buy_invoice_inventory', 'جرد فواتير الشراء'),
            ('export_buyinvoice', 'تصدير فواتير الشراء'),
            ('show_total_buyinvoice', 'عرض مجاميع فواتير الشراء'),

            ('category_return_permission', 'قسم الترجيعات'),
            ('template_return_permission_entry', 'ادخال اذن ترجيع'),
            ('template_return_reports', 'تقارير الترجيع'),
            ('export_return_permissions', 'تصدير الترجيعات'),

            ('category_clients', 'قسم العملاء'),
            ('template_customer_guide', 'دليل العملاء'),
            ('template_customer_reports', 'تقارير العملاء'),
            ('template_account_settlement', 'تسوية حساب العملاء'),
            ('template_account_settlement_reports', 'تقارير تسوية حساب العملاء'),
            ('template_audit_reports', 'تقارير المراجعة للعملاء'),
            ('edit_account_statement_clients', 'تعديل كشف الحساب للعملاء'),
            ('export_clients', 'تصدير العملاء'),
            ('show_total_clients', 'عرض مجاميع العملاء'),

            ('category_suppliers', 'قسم الموردين'),
            ('template_add_supplier', 'اضافة مورد'),
            ('template_supplier_reports', 'تقارير الموردين'),
            ('template_supplier_guide', 'دليل الموردين'),
            ('template_supplier_account_settlement', 'تسوية حساب الموردين'),
            ('template_supplier_account_settlement_reports', 'تقارير تسوية حساب الموردين'),
            ('template_audit_reports_suppliers', 'تقارير المراجعة للموردين'),
            ('edit_account_statement_suppliers', 'تعديل كشف الحساب للموردين'),
            ('export_suppliers', 'تصدير الموردين'),
            ('show_total_suppliers', 'عرض مجاميع الموردين'),

            ('category_employees', 'قسم الموظفين'),
            ('template_employee_directory', 'دليل الموظفين'),
            ('template_drivers', 'الموصلين'),
            ('template_salary_accounts', 'حساب المرتبات'),
            ('template_settlement_entries', 'قيود التسوية'),
            ('template_emp_reports', 'تقارير الموظفين'),
            ('template_settlement_reports', 'تقارير التسوية'),
            ('template_attendance_absence', 'حضور وغياب'),
            ('edit_account_employees', 'تعديل حساب الموظفين'),
            ('export_employees', 'تصدير الموظفين'),
            ('allow_over_salary_depts_employees', 'السماح بالصرف بتجاوز المرتب للموظف'),

            ('category_storage', 'قسم الخزينة'),
            ('template_treasury_entries', 'قيود الخزينة'),
            ('template_treasury_reports', 'تقارير الخزينة'),
            ('template_request_value', 'طلب قيمة من الخزينة'),
            ('template_treasury_movements', 'حركة الخزينة'),
            ('export_treasury', 'تصدير بيانات الخزينة'),
            ('show_withdraw_records_treasury', 'عرض قيود صرف من الخزينة'),
            ('add_withdraw_records_treasury', 'ادخال قيود صرف للخزينة'),

            ('category_users', 'قسم المستخدمين'),
            ('template_users_management', 'ادارة المستخدمين'),
            ('show_statistics', 'عرض الاحصائيات'),
        ]

class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BuyInvoiceItemsTable(models.Model):
    autoid = models.BigAutoField(primary_key=True)
    item_no = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    pno = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    name = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    company = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    company_no = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    quantity_unit = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    currency = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    date = models.CharField(max_length=30, db_collation='Arabic_CI_AS', blank=True, null=True)
    place = models.CharField(max_length=30, db_collation='Arabic_CI_AS', blank=True, null=True)
    buysource = models.CharField(max_length=250, db_collation='Arabic_CI_AS', blank=True, null=True)
    org_unit_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    org_total_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    dinar_unit_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    dinar_total_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    cost_unit_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    cost_total_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    note = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    barcodeno = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    e_name = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    prev_quantity = models.IntegerField(blank=True, null=True)
    prev_cost_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    prev_buy_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    prev_less_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    current_quantity = models.IntegerField(blank=True, null=True)
    current_cost_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    current_buy_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    current_less_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    invoice_no = models.ForeignKey(Buyinvoicetable, models.DO_NOTHING)
    invoice_no2 = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    main_cat = models.CharField(max_length=70, db_collation='Arabic_CI_AS', blank=True, null=True)
    sub_cat = models.CharField(max_length=70, db_collation='Arabic_CI_AS', blank=True, null=True)
    source = models.ForeignKey('AllSourcesTable', on_delete=models.CASCADE, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'buy_invoice_items_table'


class Clienttypestable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    tname = models.CharField(db_column='TName', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'clientTypesTable'


class CostTypesTable(models.Model):
    autoid = models.AutoField(primary_key=True)
    cost_for = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cost_types_Table'

class CurrenciesTable(models.Model):
    autoid = models.AutoField(primary_key=True)
    currency = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'currenciesTable'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(db_collation='Arabic_CI_AS', blank=True, null=True)
    object_repr = models.CharField(max_length=200, db_collation='Arabic_CI_AS')
    action_flag = models.SmallIntegerField()
    change_message = models.TextField(db_collation='Arabic_CI_AS')
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100, db_collation='Arabic_CI_AS')
    model = models.CharField(max_length=100, db_collation='Arabic_CI_AS')

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255, db_collation='Arabic_CI_AS')
    name = models.CharField(max_length=255, db_collation='Arabic_CI_AS')
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40, db_collation='Arabic_CI_AS')
    session_data = models.TextField(db_collation='Arabic_CI_AS')
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Maintypetable(models.Model):
    fileid = models.BigAutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    typename = models.CharField(db_column='TypeName', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    logo_obj = models.ImageField(upload_to='logos/', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'mainTypeTable'

    def __str__(self):
        return str(self.fileid) + " | " + (self.typename if self.typename else "Unnamed Subtype")


class Manufaccountrytable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    countryname = models.CharField(db_column='countryName', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'manufacCountryTable'


class MeasurementsTable(models.Model):
    name = models.CharField(max_length=100, db_collation='Arabic_CI_AS')

    class Meta:
        managed = True
        db_table = 'measurements'


class Modeltable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    model_name = models.CharField(db_column='Model_name', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    subtype_fk = models.ForeignKey("Subtypetable", models.CASCADE)

    class Meta:
        managed = True
        db_table = 'modelTable'
    def __str__(self):
        return str(self.fileid) + " | " + str(self.subtype_fk.subtypename) + " - " + (self.model_name if self.model_name else "Unnamed model")


class Productnametable(models.Model):
    fileid = models.BigAutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    typename = models.CharField(db_column='TypeName', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'productNameTable'





class Subtypetable(models.Model):
    fileid = models.BigAutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    subtypename = models.CharField(db_column='SubTypeName', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maintype_fk = models.ForeignKey(Maintypetable, models.CASCADE)

    class Meta:
        managed = True
        db_table = 'subTypeTable'

    def __str__(self):
        return str(self.fileid) + " | " + str(self.maintype_fk.typename) + " - " + (self.subtypename if self.subtypename else "Unnamed Subtype")

class enginesTable(models.Model):
    fileid = models.BigAutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    engine_name = models.CharField(db_column='SubTypeName', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maintype_str = models.CharField(max_length=800 ,null=True ,blank=True)
    subtype_str = models.CharField(max_length=800 ,null=True ,blank=True)

    class Meta:
        managed = True
        db_table = 'enginesTable'

    def __str__(self):
        return str(self.fileid) + " | " + (self.engine_name if self.engine_name else "Unnamed engine")

class TransactionsHistoryTable(models.Model):
    autoid = models.AutoField(primary_key=True)
    transaction = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    debt = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    credit = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    details = models.CharField(max_length=400, db_collation='Arabic_CI_AS', blank=True, null=True)
    registration_date = models.DateTimeField(blank=True, null=True)
    delivered_date = models.DateTimeField(blank=True, null=True)
    delivered_for = models.CharField(max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)
    current_balance = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)

    # Generic foreign key fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    client_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        managed = True
        db_table = 'transactions_history_Table'


class SellInvoiceItemsTable(models.Model):
    autoid = models.BigAutoField(primary_key=True)
    item_no = models.CharField(max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)
    pno = models.CharField(max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)
    name = models.CharField(max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)
    company = models.CharField(max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)
    company_no = models.CharField(max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    quantity_unit = models.CharField(max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)
    date = models.CharField(max_length=130, db_collation='Arabic_CI_AS', blank=True, null=True)
    place = models.CharField(max_length=130, db_collation='Arabic_CI_AS', blank=True, null=True)
    dinar_unit_price = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    dinar_total_price = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    note = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    e_name = models.CharField(max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)
    prev_quantity = models.IntegerField(blank=True, null=True)
    current_quantity = models.IntegerField(blank=True, null=True)
    current_quantity_after_return = models.IntegerField(blank=True, null=True)
    invoice_instance = models.ForeignKey(SellinvoiceTable, models.DO_NOTHING)
    invoice_no = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    main_cat = models.CharField(max_length=170, db_collation='Arabic_CI_AS', blank=True, null=True)
    sub_cat = models.CharField(max_length=170, db_collation='Arabic_CI_AS', blank=True, null=True)
    paid = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    remaining = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    returned = models.DecimalField(max_digits=19, decimal_places=4, default=0)

    class Meta:
        managed = True
        db_table = 'sell_invoice_items_table'



class EmployeesTable(models.Model):
    employee_id = models.BigAutoField(primary_key=True)
    name = models.CharField(blank=True, null=True, max_length=100)
    identity_doc = models.CharField(blank=True, null=True, max_length=200)
    nationality = models.CharField(blank=True, null=True, max_length=200)
    last_transaction = models.CharField(blank=True, null=True, max_length=200)
    salary = models.DecimalField(max_digits=19,decimal_places=4,default=0)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    daily_start_time = models.TimeField(
        default=datetime.time(9, 0)
    )
    daily_end_time = models.TimeField(
        default=datetime.time(18, 0)
    )
    active = models.BooleanField(default=True)
    category = models.CharField(blank=True, null=True, max_length=50)
    notes = models.CharField(blank=True, null=True, max_length=300)
    phone = models.CharField(max_length=100,unique=True)
    address = models.CharField(blank=True, null=True, max_length=100)
    bank_details = models.CharField(blank=True, null=True, max_length=200)
    bank_account_no = models.CharField(blank=True, null=True, max_length=100)
    bank_iban_no = models.CharField(blank=True, null=True, max_length=100)
    is_available = models.BooleanField(default=True)
    has_active_order = models.BooleanField(default=False)
    fcm_token = models.TextField(null=True, blank=True)


    # New fields
    username = models.CharField(max_length=150, unique=True,null=True)  # Ensure username is unique
    password = models.CharField(max_length=255,null=True)  # This will store the hashed password

    class Meta:
        managed = True
        db_table = 'Employees_table'

    def set_password(self, raw_password):
        """Hashes the password before saving."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Checks if the given raw password matches the stored hash."""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

class ChatMessage(models.Model):
    sender = models.ForeignKey('AllClientsTable', on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey('AllClientsTable', on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(default=now)  # ❌ Incorrect usage

    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"



class SupportChatConversation(models.Model):
    """
    Represents a conversation between a client and a support agent.
    Both sides are represented by the AllClientsTable.
    """
    conversation_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(
        'AllClientsTable',
        on_delete=models.CASCADE,
        related_name='client_conversations'
    )
    support_agent = models.ForeignKey(
        'AllClientsTable',
        on_delete=models.CASCADE,
        related_name='support_conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'support_chat_conversation'
        unique_together = (('client', 'support_agent'),)

    def __str__(self):
        return f"Conversation: {self.client.username} & {self.support_agent.username}"


class SupportChatMessageSys(models.Model):
    """
    Stores individual messages within a support chat conversation.
    """
    message_id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(
        SupportChatConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        'AllClientsTable',
        on_delete=models.CASCADE,
        related_name='sent_support_messages'
    )
    # sender_type explicitly marks whether the sender is a 'client' or 'support'
    sender_type = models.CharField(
        max_length=10,
        choices=(('client', 'Client'), ('support', 'Support')),
        default='client'
    )
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'support_chat_message_sys'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username} ({self.sender_type}) at {self.timestamp}"


class Feedback(models.Model):
    sender = models.ForeignKey(AllClientsTable, related_name="sent_feedback", on_delete=models.CASCADE)
    feedback_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_resolved = models.BooleanField(default=False)
    parent_feedback = models.ForeignKey('self', related_name='replies', null=True, blank=True, on_delete=models.SET_NULL)
    employee_response = models.TextField(blank=True, null=True)  # Added for employee to respond to feedback
    response_at = models.DateTimeField(null=True, blank=True)  # The time the employee responded

    def __str__(self):
        return f"Feedback from {self.sender.name} to {self.receiver.name} at {self.created_at}"

class FeedbackMessage(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name="messages")
    sender_type = models.CharField(max_length=10, choices=[('client', 'Client'), ('employee', 'Employee')])
    message_text = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message in Feedback {self.feedback.id}"


class return_permission(models.Model):
    autoid = models.AutoField(primary_key=True)
    client=models.ForeignKey(AllClientsTable,on_delete=models.CASCADE)
    employee=models.CharField(max_length=200,null=True,blank=True)
    date = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(default=0)
    invoice_obj = models.ForeignKey(SellinvoiceTable,on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200,null=True,blank=True)
    amount = models.DecimalField(default=0,max_digits=19,decimal_places=4)
    payment = models.CharField(max_length=150,default='نقدي')

    def __str__(self):
        return str(self.autoid) + "- invoice: " + str(self.invoice_obj.invoice_no) + "- amount: " + str(self.amount)

class return_permission_items(models.Model):
    autoid = models.AutoField(primary_key=True)
    pno = models.IntegerField(blank=True,null=True)
    company_no = models.CharField(max_length=200,null=True,blank=True)
    company = models.CharField(max_length=200,null=True,blank=True)
    item_name = models.CharField(max_length=200,null=True,blank=True)
    org_quantity = models.IntegerField(blank=True,null=True)
    returned_quantity = models.IntegerField(blank=True,null=True)
    price = models.DecimalField(max_digits=19,decimal_places=4,null=False)
    total = models.DecimalField(max_digits=19,decimal_places=4,null=False)
    invoice_obj = models.ForeignKey(SellinvoiceTable,on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=40,null=True,blank=True)
    permission_obj = models.ForeignKey(return_permission,on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Ensure total is always calculated as returned_quantity * price
        self.total = (self.returned_quantity or 0) * (self.price or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} - {self.total}"


class PaymentRequestTable(models.Model):
    autoid = models.AutoField(primary_key=True)
    client = models.ForeignKey(AllClientsTable,on_delete=models.CASCADE)
    requested_amount = models.DecimalField(max_digits=19,decimal_places=4)
    accepted_amount = models.DecimalField(max_digits=19,decimal_places=4,default=0)
    employee = models.CharField(max_length=100, null=True, blank=True)
    issue_date = models.DateField(auto_now_add=True)
    accept_date = models.DateField(null=True)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        return str(self.autoid) +' | '+ self.client.name + ' | '+ str(self.requested_amount)

class DeliveryQueue(models.Model):
    order = models.ForeignKey(SellinvoiceTable, on_delete=models.CASCADE, related_name='delivery_queue')
    employee = models.ForeignKey(EmployeesTable, on_delete=models.CASCADE, related_name='assigned_orders')
    order_assigned_at = models.DateTimeField(default=timezone.now)
    order_delivered_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('delivered', 'Delivered')], default='pending')
    queue_number = models.PositiveIntegerField(default=1)  # Track the queue number

    def assign_order(self):
        """Assign the order to the first available delivery person with queue_number 1."""
        available_employee = EmployeesTable.objects.filter(is_available=True).first()

        if available_employee:
            self.employee = available_employee
            self.status = 'pending'
            self.employee.is_available = False  # Mark the employee as unavailable
            self.employee.save()
            self.save()

            # Reassign the queue number and update position in the queue
            next_queue = DeliveryQueue.objects.filter(queue_number__gte=1).order_by('queue_number')
            self.queue_number = next_queue.last().queue_number + 1 if next_queue.exists() else 1
            self.save()

            # Move the employee to the last position in the queue after they take the order
            DeliveryQueue.objects.filter(employee=available_employee).update(queue_number=self.queue_number)

            return f"Order {self.order.autoid} assigned to {available_employee.name}."
        return "No available delivery person."

    def mark_delivered(self):
        """Mark the order as delivered and make the delivery person available again."""
        self.status = 'delivered'
        self.order_delivered_at = timezone.now()
        self.employee.is_available = True  # Make the employee available again
        self.employee.save()
        self.save()

        # Move the employee to the last position in the queue
        self.employee.is_available = False
        self.save()

        return f"Order {self.order.autoid} has been delivered by {self.employee.name}."

    class Meta:
        db_table = 'DeliveryQueue'




# Assume EmployeeTable is already defined
# Add a Queue Table if not already
class EmployeeQueue(models.Model):
    employee = models.ForeignKey(EmployeesTable, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()  # Position in the queue
    is_assigned = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)  # To check if the employee is available
    assigned_time = models.DateTimeField(null=True, blank=True)  # Track when order was assigned


class OrderQueue(models.Model):
    order = models.ForeignKey(SellinvoiceTable, on_delete=models.CASCADE)
    employee = models.ForeignKey(EmployeesTable, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)  # Add this field
    is_declined = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)  # Track if the order is completed
    assigned_at = models.DateTimeField(default=timezone.now) # Store assignment time
    is_assigned = models.BooleanField(default=False)
from django.db import models

class OrderArchive(models.Model):
    order = models.ForeignKey('SellinvoiceTable', on_delete=models.CASCADE)  # Reference to the original order
    employee = models.ForeignKey('EmployeesTable', on_delete=models.CASCADE)  # Employee who completed the order
    delivery_status = models.CharField(max_length=255)  # Delivery status (e.g., 'تم التسليم')
    is_completed = models.BooleanField(default=False)  # Status of completion
    order_date = models.DateTimeField(auto_now_add=True)  # Timestamp when the order was archived
    completion_date = models.DateTimeField(auto_now=True)  # Timestamp when the order was completed

    def __str__(self):
        return f"Order {self.order.id} completed by {self.employee.name}"




class CartItem(models.Model):
    # Link cart item to a client using ForeignKey
    client = models.ForeignKey('AllClientsTable', on_delete=models.CASCADE, related_name='cart_items')

    fileid = models.CharField(max_length=255)
    itemname = models.CharField(max_length=255)
    buyprice = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    image = models.URLField(max_length=500, blank=True, null=True)
    logo = models.URLField(max_length=500, blank=True, null=True)
    pno = models.CharField(max_length=50, blank=True, null=True)
    itemvalue = models.PositiveIntegerField()

    class Meta:
        unique_together = ('client', 'fileid')  # Ensure the same item isn't duplicated for a client

    def __str__(self):
        return f"{self.client.name} - {self.itemname} (x{self.quantity})"


class balance_editions(models.Model):
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmployeesTable,on_delete=models.CASCADE)
    name = models.CharField(max_length=300, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=19, decimal_places=9)
    balance_before = models.DecimalField(max_digits=19, decimal_places=9,null=True, blank=True)
    balance_after = models.DecimalField(max_digits=19, decimal_places=9,null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.employee.name} - {self.type} {self.amount} LYD"


class Attendance_table(models.Model):
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmployeesTable,on_delete=models.CASCADE)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date = models.DateField()
    daily_hours = models.DecimalField(max_digits=10, decimal_places=2, default=6.0)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    worked_hours = models.DecimalField(max_digits=10, decimal_places=2, default=6.0)
    absent_hours = models.DecimalField(max_digits=10, decimal_places=2, default=6.0)
    coming_time = models.TimeField(null=True, blank=True)
    leaving_time = models.TimeField(null=True, blank=True)
    absent = models.BooleanField(default=False)
    reason = models.CharField(max_length=400, null=True, blank=True)
    note = models.CharField(max_length=400, null=True, blank=True)

#  hozma models
class PreOrderTable(models.Model):
    autoid = models.AutoField(primary_key=True)
    client = models.ForeignKey(AllClientsTable, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=200, blank=True, null=True)
    invoice_no = models.IntegerField(unique=True)
    invoice_date = models.DateTimeField(blank=True, null=True)
    client_rate = models.CharField(max_length=60, blank=True, null=True)
    client_category = models.CharField(max_length=60, blank=True, null=True)
    client_limit = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    client_balance = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    payment_status = models.CharField(max_length=60, blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    mobile = models.BooleanField(default=False)
    invoice_status = models.CharField(max_length=60, default="قيد المراجعة")
    reviewed_by = models.CharField(max_length=100, blank=True, null=True)
    reviewed_date = models.DateTimeField(blank=True, null=True)
    is_reviewed = models.BooleanField(default=False)
    is_confirmed_by_client = models.BooleanField(default=False)
    is_declined_by_client = models.BooleanField(default=False)
    date_time = models.DateTimeField(default=timezone.now)
    client_confrim = models.BooleanField(default=False)
    shop_confrim = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=20, default="pending") # or "waiting", "done"
    processing_status_confirmed = models.BooleanField(default=False)


    class Meta:
        db_table = 'PreOrderTable'


class ConfirmedOrderTable(models.Model):
    autoid = models.AutoField(primary_key=True)
    client = models.ForeignKey(AllClientsTable, on_delete=models.CASCADE)
    invoice_no = models.IntegerField(unique=True)
    invoice_date = models.DateTimeField(blank=True, null=True)
    client_rate = models.CharField(max_length=60, blank=True, null=True)
    client_category = models.CharField(max_length=60, blank=True, null=True)
    client_limit = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    client_balance = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    payment_status = models.CharField(max_length=60, blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    mobile = models.BooleanField(default=False)
    invoice_status = models.CharField(max_length=60, default="قيد المراجعة")
    reviewed_by = models.CharField(max_length=100, blank=True, null=True)
    reviewed_date = models.DateTimeField(blank=True, null=True)
    is_reviewed = models.BooleanField(default=False)
    is_confirmed_by_client = models.BooleanField(default=False)
    is_declined_by_client = models.BooleanField(default=False)
    date_time = models.DateTimeField(default=timezone.now)
    preorder_reference = models.ForeignKey(PreOrderTable, on_delete=models.SET_NULL, null=True)
    date_confirmed = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = 'ConfirmedOrderTable'


class ArchivedOrderTable(models.Model):
    preorder_reference = models.ForeignKey(PreOrderTable, on_delete=models.SET_NULL, null=True)

    reason = models.CharField(max_length=255, blank=True, null=True)
    date_archived = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ArchivedOrderTable'


class PreOrderItemsTable(models.Model):
    autoid = models.BigAutoField(primary_key=True)
    item_no = models.CharField(max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)
    pno = models.CharField(max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)
    name = models.CharField(max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)
    company = models.CharField(max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)
    company_no = models.CharField(max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    quantity_unit = models.CharField(max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    place = models.CharField(max_length=130, db_collation='Arabic_CI_AS', blank=True, null=True)
    dinar_unit_price = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    dinar_total_price = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    note = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    e_name = models.CharField(max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)
    prev_quantity = models.IntegerField(blank=True, null=True)
    current_quantity = models.IntegerField(blank=True, null=True)
    current_quantity_after_return = models.IntegerField(blank=True, null=True)
    invoice_instance = models.ForeignKey(PreOrderTable, models.DO_NOTHING)
    invoice_no = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    main_cat = models.CharField(max_length=170, db_collation='Arabic_CI_AS', blank=True, null=True)
    sub_cat = models.CharField(max_length=170, db_collation='Arabic_CI_AS', blank=True, null=True)
    paid = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    remaining = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    returned = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    confirm_quantity = models.IntegerField(blank=True, null=True)
    quantity_proccessed = models.BooleanField(default=False)


    class Meta:
        managed = True
        db_table = 'pre_order_items_table'

class TempBuyInvoiceItemsTable(models.Model):
    source = models.ForeignKey('AllSourcesTable', on_delete=models.CASCADE)
    item_no = models.IntegerField()
    pno = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.FloatField()
    dinar_unit_price = models.FloatField()
    dollar_unit_price = models.FloatField()
    dinar_total_price = models.FloatField()
    dollar_total_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.source} - {self.name} ({self.quantity})"
class OrderBuyinvoicetable(models.Model):
    autoid = models.AutoField(primary_key=True)
    original_no = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    invoice_date = models.DateTimeField(blank=True, null=True)
    source = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    discount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    expenses = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    net_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    account_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    arrive_date = models.DateField(blank=True, null=True)
    ready_date = models.DateField(blank=True, null=True)
    confirmation_date = models.DateField(blank=True, null=True)
    remind_before = models.IntegerField(blank=True, null=True)
    temp_flag = models.BooleanField(blank=True, null=True)
    order_no = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    multi_source_flag = models.BooleanField(blank=True, null=True)
    currency = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    invoice_no = models.IntegerField(unique=True)
    paid_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    discount_dinar = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    expenses_dinar = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    confirmed = models.BooleanField(default=False)
    send = models.BooleanField(default=False)
    send_date = models.DateTimeField(blank=True, null=True)
    source_obj = models.ForeignKey('AllSourcesTable', on_delete=models.CASCADE, blank=True, null=True)
    related_preorders = models.ManyToManyField(
        'PreOrderTable',
        blank=True,
        related_name='related_buy_invoices'
    )


    class Meta:
        managed = True
        db_table = 'OrderBuyinvoicetable'


class OrderBuyInvoiceItemsTable(models.Model):
    autoid = models.BigAutoField(primary_key=True)
    item_no = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    sourrce_pno = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    pno = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    name = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    company = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    company_no = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    Asked_quantity = models.IntegerField(blank=True, null=True)
    Confirmed_quantity = models.IntegerField(blank=True, null=True)
    quantity_unit = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    currency = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    date = models.CharField(max_length=30, db_collation='Arabic_CI_AS', blank=True, null=True)
    place = models.CharField(max_length=30, db_collation='Arabic_CI_AS', blank=True, null=True)
    buysource = models.CharField(max_length=250, db_collation='Arabic_CI_AS', blank=True, null=True)
    org_unit_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    org_total_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    dinar_unit_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    dinar_total_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    cost_unit_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    cost_total_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    note = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    barcodeno = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    e_name = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    prev_quantity = models.IntegerField(blank=True, null=True)
    prev_cost_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    prev_buy_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    prev_less_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    current_quantity = models.IntegerField(blank=True, null=True)
    current_cost_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    current_buy_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    current_less_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    invoice_no = models.ForeignKey(OrderBuyinvoicetable, models.DO_NOTHING)
    invoice_no2 = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    main_cat = models.CharField(max_length=70, db_collation='Arabic_CI_AS', blank=True, null=True)
    sub_cat = models.CharField(max_length=70, db_collation='Arabic_CI_AS', blank=True, null=True)
    source = models.ForeignKey('AllSourcesTable', on_delete=models.CASCADE, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'Orderbuy_invoice_items_table'


class Mainitem_copy(models.Model):
    fileid = models.BigAutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    itemno = models.CharField(db_column='ItemNo', max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemmain = models.CharField(db_column='ItemMain', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemsubmain = models.CharField(db_column='ItemSubMain', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    short_name = models.CharField(db_column='ShortName', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemthird = models.CharField(db_column='ItemThird', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemsize = models.CharField(db_column='ItemSize', max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    companyproduct = models.CharField(db_column='CompanyProduct', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    dateproduct = models.CharField(db_column='DateProduct', max_length=110, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    levelproduct = models.CharField(db_column='LevelProduct', max_length=110, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemvalue = models.IntegerField(db_column='ItemValue', default=0)  # Field name made lowercase.
    itemtemp = models.IntegerField(db_column='ItemTemp', default=0)  # Field name made lowercase.
    itemplace = models.CharField(db_column='ItemPlace', max_length=110, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orderlastdate = models.DateTimeField(db_column='OrderLastDate', blank=True, null=True)  # Field name made lowercase.
    ordersource = models.CharField(db_column='OrderSource', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orderbillno = models.CharField(db_column='OrderBillNo', max_length=110, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    buylastdate = models.DateTimeField(db_column='buyLastdate', blank=True, null=True)  # Field name made lowercase.
    buysource = models.CharField(db_column='BuySource', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    buybillno = models.CharField(db_column='BuyBillNo', max_length=110, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orgprice = models.DecimalField(db_column='OrgPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    orderprice = models.DecimalField(db_column='OrderPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    costprice = models.DecimalField(db_column='CostPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    buyprice = models.DecimalField(db_column='BuyPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    memo = models.CharField(db_column='Memo', max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orderstop = models.BooleanField(db_column='OrderStop', blank=True, null=True)  # Field name made lowercase.
    buystop = models.BooleanField(db_column='BuyStop', blank=True, null=True)  # Field name made lowercase.
    itemtrans = models.BooleanField(db_column='ItemTrans', blank=True, null=True)  # Field name made lowercase.
    itemvalueb = models.IntegerField(db_column='ItemValueB', blank=True, null=True)  # Field name made lowercase.
    replaceno = models.CharField(db_column='ReplaceNo', max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemtype = models.CharField(db_column='ItemType', max_length=115, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    barcodeno = models.CharField(db_column='BarcodeNo', max_length=125, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    eitemname = models.CharField(db_column='EItemName', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    currtype = models.CharField(db_column='CurrType', max_length=115, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    lessprice = models.DecimalField(db_column='LessPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    pno = models.IntegerField(db_column='PNo', blank=False, null=False, unique=True)  # Field name made lowercase.
    currvalue = models.DecimalField(db_column='CurrValue', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    resvalue = models.IntegerField(db_column='resValue', blank=True, null=True)  # Field name made lowercase.
    itemperbox = models.IntegerField(db_column='ItemPerbox', blank=True, null=True)  # Field name made lowercase.
    cstate = models.IntegerField(db_column='CSTate', blank=True, null=True)  # Field name made lowercase.
    oem_numbers = models.CharField(max_length=1000, blank=True, null=True)
    engine_no = models.CharField(max_length=300, blank=True, null=True)
    json_description = models.JSONField(null=True,blank=True)
    showed = models.IntegerField(default=0)
    source_pno = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
     # Adding the foreign key to AllSourcesTable is for HOZMA ATTENTIN IS FOR HOZMA
    source = models.ForeignKey('AllSourcesTable', on_delete=models.CASCADE, blank=True, null=True)
    category = models.CharField(db_column='category', max_length=150, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    discount = models.DecimalField(db_column='discount', max_digits=19, decimal_places=4, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'MainItem_copy'