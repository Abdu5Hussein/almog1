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
    permissions = models.CharField(max_length=400, db_collation='Arabic_CI_AS', blank=True, null=True)
    other = models.CharField(max_length=400, db_collation='Arabic_CI_AS', blank=True, null=True)
    last_transaction_details = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    last_transaction_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    geo_location = models.CharField(max_length=200, blank=True, null=True)
    # New fields
    username = models.CharField(max_length=150, unique=True,null=False)  # Ensure username is unique
    password = models.CharField(max_length=255,null=False)  # This will store the hashed password

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
        managed = False
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

    class Meta:
        managed = True
        db_table = 'BuyInvoiceTable'

class SellinvoiceTable(models.Model):
    autoid = models.AutoField(primary_key=True)
    invoice_date = models.DateTimeField(blank=True, null=True)
    client = models.CharField(max_length=30, db_collation='Arabic_CI_AS', blank=True, null=True)
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
    itemno = models.CharField(db_column='ItemNo', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemmain = models.CharField(db_column='ItemMain', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemsubmain = models.CharField(db_column='ItemSubMain', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    short_name = models.CharField(db_column='ShortName', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemthird = models.CharField(db_column='ItemThird', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemsize = models.CharField(db_column='ItemSize', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    companyproduct = models.CharField(db_column='CompanyProduct', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    dateproduct = models.CharField(db_column='DateProduct', max_length=10, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    levelproduct = models.CharField(db_column='LevelProduct', max_length=10, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemvalue = models.IntegerField(db_column='ItemValue', blank=True, null=True)  # Field name made lowercase.
    itemtemp = models.IntegerField(db_column='ItemTemp', blank=True, null=True)  # Field name made lowercase.
    itemplace = models.CharField(db_column='ItemPlace', max_length=10, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orderlastdate = models.DateTimeField(db_column='OrderLastDate', blank=True, null=True)  # Field name made lowercase.
    ordersource = models.CharField(db_column='OrderSource', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orderbillno = models.CharField(db_column='OrderBillNo', max_length=10, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    buylastdate = models.DateTimeField(db_column='buyLastdate', blank=True, null=True)  # Field name made lowercase.
    buysource = models.CharField(db_column='BuySource', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    buybillno = models.CharField(db_column='BuyBillNo', max_length=10, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orgprice = models.DecimalField(db_column='OrgPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    orderprice = models.DecimalField(db_column='OrderPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    costprice = models.DecimalField(db_column='CostPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    buyprice = models.DecimalField(db_column='BuyPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    memo = models.CharField(db_column='Memo', max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orderstop = models.BooleanField(db_column='OrderStop', blank=True, null=True)  # Field name made lowercase.
    buystop = models.BooleanField(db_column='BuyStop', blank=True, null=True)  # Field name made lowercase.
    itemtrans = models.BooleanField(db_column='ItemTrans', blank=True, null=True)  # Field name made lowercase.
    itemvalueb = models.IntegerField(db_column='ItemValueB', blank=True, null=True)  # Field name made lowercase.
    replaceno = models.CharField(db_column='ReplaceNo', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    itemtype = models.CharField(db_column='ItemType', max_length=15, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    barcodeno = models.CharField(db_column='BarcodeNo', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    eitemname = models.CharField(db_column='EItemName', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    currtype = models.CharField(db_column='CurrType', max_length=5, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    lessprice = models.DecimalField(db_column='LessPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    pno = models.IntegerField(db_column='PNo', blank=False, null=False, unique=True)  # Field name made lowercase.
    currvalue = models.DecimalField(db_column='CurrValue', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    resvalue = models.IntegerField(db_column='resValue', blank=True, null=True)  # Field name made lowercase.
    itemperbox = models.IntegerField(db_column='ItemPerbox', blank=True, null=True)  # Field name made lowercase.
    cstate = models.IntegerField(db_column='CSTate', blank=True, null=True)  # Field name made lowercase.
    oem_numbers = models.CharField(max_length=1000, blank=True, null=True)
    engine_no = models.CharField(max_length=300, blank=True, null=True)

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
    oemno = models.CharField(db_column='OEMNO', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
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
        managed = False
        db_table = 'TTable'


class Tablerights(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TableRights'


class Titletable(models.Model):
    fileid = models.BigAutoField(db_column='Fileid', primary_key=True)  # Field name made lowercase.
    titlename = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
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

    class Meta:
        managed = True
        db_table = 'mainTypeTable'

    def __str__(self):
        return str(self.fileid) + " | " + (self.typename if self.typename else "Unnamed Subtype")


class Manufaccountrytable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    countryname = models.CharField(db_column='countryName', max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'manufacCountryTable'


class MeasurementsTable(models.Model):
    name = models.CharField(max_length=100, db_collation='Arabic_CI_AS')

    class Meta:
        managed = False
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
        managed = False
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
    client_id = models.ForeignKey(AllClientsTable, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'transactions_history_Table'


class SellInvoiceItemsTable(models.Model):
    autoid = models.BigAutoField(primary_key=True)
    item_no = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    pno = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    name = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    company = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    company_no = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    quantity_unit = models.CharField(max_length=25, db_collation='Arabic_CI_AS', blank=True, null=True)
    date = models.CharField(max_length=30, db_collation='Arabic_CI_AS', blank=True, null=True)
    place = models.CharField(max_length=30, db_collation='Arabic_CI_AS', blank=True, null=True)
    dinar_unit_price = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    dinar_total_price = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    note = models.CharField(max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)
    e_name = models.CharField(max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    prev_quantity = models.IntegerField(blank=True, null=True)
    current_quantity = models.IntegerField(blank=True, null=True)
    invoice_instance = models.ForeignKey(SellinvoiceTable, models.DO_NOTHING)
    invoice_no = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    main_cat = models.CharField(max_length=70, db_collation='Arabic_CI_AS', blank=True, null=True)
    sub_cat = models.CharField(max_length=70, db_collation='Arabic_CI_AS', blank=True, null=True)
    paid = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    remaining = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    returned = models.DecimalField(max_digits=19, decimal_places=4, default=0)

    class Meta:
        managed = True
        db_table = 'sell_invoice_items_table'



class EmployeesTable(models.Model):
    employee_id = models.BigAutoField(primary_key=True)
    name = models.CharField(blank=True, null=True, max_length=100)
    salary = models.DecimalField(max_digits=19,decimal_places=4,default=0)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)
    category = models.CharField(blank=True, null=True, max_length=50)
    notes = models.CharField(blank=True, null=True, max_length=300)
    phone = models.CharField(blank=True, null=True, max_length=100)
    address = models.CharField(blank=True, null=True, max_length=100)
    bank_details = models.CharField(blank=True, null=True, max_length=200)
    bank_account_no = models.CharField(blank=True, null=True, max_length=100)
    bank_iban_no = models.CharField(blank=True, null=True, max_length=100)

    # New fields
    username = models.CharField(max_length=150, unique=True,null=False)  # Ensure username is unique
    password = models.CharField(max_length=255,null=False)  # This will store the hashed password

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
    quantity = models.IntegerField(blank=True,null=True)
    invoice_obj = models.ForeignKey(SellinvoiceTable,on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200,null=True,blank=True)
    amount = models.DecimalField(default=0,max_digits=19,decimal_places=4)
    payment = models.CharField(max_length=150,default='نقدي')

    def __str__(self):
        return str(self.autoid) + "- invoice: " + str(self.invoice.invoice_no) + "- amount: " + str(self.amount)

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

    def save(self, *args, **kwargs):
        # Ensure total is always calculated as returned_quantity * price
        self.total = (self.returned_quantity or 0) * (self.price or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} - {self.total}"