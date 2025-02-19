# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Blancetable(models.Model):
    fileid = models.IntegerField(db_column='FileId')  # Field name made lowercase.
    itemid = models.IntegerField(db_column='ItemId', blank=True, null=True)  # Field name made lowercase.
    itemno = models.CharField(db_column='ItemNo', max_length=25, blank=True, null=True)  # Field name made lowercase.
    itemmain = models.CharField(db_column='ItemMain', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemvalue = models.IntegerField(db_column='ItemValue', blank=True, null=True)  # Field name made lowercase.
    tdate = models.DateTimeField(db_column='TDate', blank=True, null=True)  # Field name made lowercase.
    tname = models.CharField(db_column='TName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tno = models.CharField(db_column='TNo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tvalue = models.IntegerField(db_column='TValue', blank=True, null=True)  # Field name made lowercase.
    ttype = models.IntegerField(db_column='TType', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BlanceTable'


class Companytable(models.Model):
    fileid = models.BigAutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    companyname = models.CharField(db_column='CompanyName', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CompanyTable'


class Mainitem(models.Model):
    fileid = models.BigAutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    itemno = models.CharField(db_column='ItemNo', max_length=25, blank=True, null=True)  # Field name made lowercase.
    itemmain = models.CharField(db_column='ItemMain', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemsubmain = models.CharField(db_column='ItemSubMain', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemthird = models.CharField(db_column='ItemThird', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemsize = models.CharField(db_column='ItemSize', max_length=25, blank=True, null=True)  # Field name made lowercase.
    companyproduct = models.CharField(db_column='CompanyProduct', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dateproduct = models.CharField(db_column='DateProduct', max_length=10, blank=True, null=True)  # Field name made lowercase.
    levelproduct = models.CharField(db_column='LevelProduct', max_length=10, blank=True, null=True)  # Field name made lowercase.
    itemvalue = models.IntegerField(db_column='ItemValue', blank=True, null=True)  # Field name made lowercase.
    itemtemp = models.IntegerField(db_column='ItemTemp', blank=True, null=True)  # Field name made lowercase.
    itemplace = models.CharField(db_column='ItemPlace', max_length=10, blank=True, null=True)  # Field name made lowercase.
    orderlastdate = models.DateTimeField(db_column='OrderLastDate', blank=True, null=True)  # Field name made lowercase.
    ordersource = models.CharField(db_column='OrderSource', max_length=50, blank=True, null=True)  # Field name made lowercase.
    orderbillno = models.CharField(db_column='OrderBillNo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    buylastdate = models.DateTimeField(db_column='buyLastdate', blank=True, null=True)  # Field name made lowercase.
    buysource = models.CharField(db_column='BuySource', max_length=50, blank=True, null=True)  # Field name made lowercase.
    buybillno = models.CharField(db_column='BuyBillNo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    orgprice = models.DecimalField(db_column='OrgPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    orderprice = models.DecimalField(db_column='OrderPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    costprice = models.DecimalField(db_column='CostPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    buyprice = models.DecimalField(db_column='BuyPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    memo = models.CharField(db_column='Memo', max_length=200, blank=True, null=True)  # Field name made lowercase.
    orderstop = models.BooleanField(db_column='OrderStop', blank=True, null=True)  # Field name made lowercase.
    buystop = models.BooleanField(db_column='BuyStop', blank=True, null=True)  # Field name made lowercase.
    itemtrans = models.BooleanField(db_column='ItemTrans', blank=True, null=True)  # Field name made lowercase.
    itemvalueb = models.IntegerField(db_column='ItemValueB', blank=True, null=True)  # Field name made lowercase.
    replaceno = models.CharField(db_column='ReplaceNo', max_length=25, blank=True, null=True)  # Field name made lowercase.
    itemtype = models.CharField(db_column='ItemType', max_length=15, blank=True, null=True)  # Field name made lowercase.
    barcodeno = models.CharField(db_column='BarcodeNo', max_length=25, blank=True, null=True)  # Field name made lowercase.
    eitemname = models.CharField(db_column='EItemName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    currtype = models.CharField(db_column='CurrType', max_length=5, blank=True, null=True)  # Field name made lowercase.
    lessprice = models.DecimalField(db_column='LessPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    pno = models.CharField(db_column='PNo', max_length=25, blank=True, null=True)  # Field name made lowercase.
    currvalue = models.DecimalField(db_column='CurrValue', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    resvalue = models.IntegerField(db_column='resValue', blank=True, null=True)  # Field name made lowercase.
    itemperbox = models.IntegerField(db_column='ItemPerbox', blank=True, null=True)  # Field name made lowercase.
    cstate = models.IntegerField(db_column='CSTate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'MainItem'
        indexes = [
            models.Index(
                fields=['companyproduct', 'itemmain', 'itemsubmain', 'itemname'], 
                name='MainItem_Company_a6e46b_idx'
            ),
            models.Index(
                fields=['companyproduct', 'itemmain'], 
                name='MainItem_Company_3aac0c_idx'
            ),
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
        ]


class Oemtable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    cname = models.CharField(db_column='CName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cno = models.CharField(db_column='CNo', max_length=25, blank=True, null=True)  # Field name made lowercase.
    oemno = models.CharField(db_column='OEMNO', max_length=25, blank=True, null=True)  # Field name made lowercase.
    

    class Meta:
        managed = False
        db_table = 'OEMTable'



class Clients(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    pno= models.ForeignKey(Mainitem, on_delete=models.DO_NOTHING)
    itemno = models.CharField(db_column='itemno', max_length=50, blank=True, null=True)  # Field name made lowercase.
    maintype = models.CharField(db_column='maintype', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='itemname', max_length=200, blank=True, null=True)  # Field name made lowercase.
    currentbalance = models.IntegerField(db_column='currentbalance',  blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='date', blank=True, null=True)
    clientname = models.CharField(db_column='clientname', max_length=25, blank=True, null=True)  # Field name made lowercase.
    billno = models.CharField(db_column='billno', max_length=25, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='description', max_length=25, blank=True, null=True)  # Field name made lowercase.
    clientbalance = models.IntegerField(db_column='clientbalance', blank=True, null=True)  # Field name made lowercase.
    
    
    class Meta:
        managed = True
        db_table = 'ClientsTable'

class LostAndDamaged(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    pno= models.ForeignKey(Mainitem, on_delete=models.DO_NOTHING)
    pno_value = models.CharField(max_length=100, blank=True, null=True)  # Store actual pno value
    date = models.DateField(auto_now_add=True)
    itemno = models.CharField(db_column='ItemNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    companyno = models.CharField(db_column='CompanyNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', max_length=200, blank=True, null=True)  # Field name made lowercase.
    user = models.CharField(db_column='User', max_length=50, blank=True, null=True)  # Field name made lowercase.
    quantity = models.IntegerField(db_column='Quantity', blank=True, null=True)  # Field name made lowercase.
    company = models.CharField(db_column='Company', max_length=25, blank=True, null=True)  # Field name made lowercase.
    costprice = models.DecimalField(db_column='CostPrice', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=25, blank=True, null=True)  # Field name made lowercase.
    
    
    class Meta:
        managed = True
        db_table = 'Lost_and_damaged_Table'

class Imagetable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    productid = models.IntegerField(db_column='ProductId', blank=True, null=True)  # Field name made lowercase.
    image = models.ImageField(db_column='Image', blank=True, null=True)  # Field name made lowercase.
    

    class Meta:
        managed = True
        db_table = 'ImageTable'


class Sections(models.Model):
    autoid = models.AutoField( primary_key=True)  
    section = models.CharField( blank=True,max_length=100, null=True) 
    description = models.CharField( blank=True,max_length=300, null=True) 

    class Meta:
        managed = True
        db_table = 'SectionsTable'

class SubSections(models.Model):
    autoid = models.AutoField( primary_key=True)  
    subsection = models.CharField( blank=True,max_length=100, null=True) 
    description = models.CharField( blank=True,max_length=300, null=True) 
    sectionid = models.ForeignKey(Sections, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'subSectionsTable'

class currency(models.Model):
    autoid = models.AutoField( primary_key=True)  
    currency = models.CharField( blank=True,max_length=100, null=True) 
    exchange_rate = models.DecimalField( blank=True,max_digits=19, decimal_places=4, null=True) 
    class Meta:
        managed = True
        db_table = 'currenciesTable'

class BuyInvoiceTable(models.Model):
    autoid = models.AutoField( primary_key=True)  
    invoice_no = models.IntegerField( blank=False, null=False,unique=True)
    paid_amount = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,)
    original_no = models.CharField( blank=True,max_length=100, null=True) 
    invoice_date = models.DateTimeField( blank=True, null=True) 
    source = models.CharField( blank=True,max_length=100, null=True) 
    amount = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,) 
    discount = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,) 
    expenses = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,)
    discount_dinar = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,) 
    expenses_dinar = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,)  
    net_amount = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,) 
    account_amount = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,) 
    arrive_date = models.DateField( blank=True, null=True) 
    ready_date = models.DateField( blank=True, null=True) 
    confirmation_date = models.DateField( blank=True, null=True) 
    remind_before = models.IntegerField(blank=True, null=True)
    temp_flag = models.BooleanField(blank=True, null=True,default=False)
    order_no = models.CharField( blank=True,max_length=100, null=True) 
    multi_source_flag = models.BooleanField( blank=True, null=True,default=False)
    currency = models.CharField( blank=True,max_length=100, null=True) 
    exchange_rate = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,)  

    class Meta:
        managed = True
        db_table = 'BuyInvoiceTable'

class BuyInvoiceItems(models.Model):
    autoid = models.BigAutoField( primary_key=True)  # Field name made lowercase.
    invoice_no = models.ForeignKey(BuyInvoiceTable, on_delete=models.CASCADE)
    invoice_no2 = models.CharField( blank=True,max_length=100, null=True)
    item_no = models.CharField( max_length=25, blank=True, null=True)  # Field name made lowercase.
    main_cat = models.CharField( max_length=70, blank=True, null=True)
    sub_cat = models.CharField( max_length=70, blank=True, null=True)  # Field name made lowercase.
    pno=models.CharField( max_length=25, blank=True, null=True)
    name = models.CharField( max_length=50, blank=True, null=True)  # Field name made lowercase.
    company = models.CharField( max_length=50, blank=True, null=True)  # Field name made lowercase.
    company_no = models.CharField( max_length=50, blank=True, null=True)
    quantity = models.IntegerField(null=True,blank=True)
    quantity_unit = models.CharField( max_length=25, blank=True, null=True)
    currency = models.CharField( max_length=25, blank=True, null=True)
    exchange_rate = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,)
    date = models.CharField( max_length=30, blank=True, null=True)  # Field name made lowercase.
    place = models.CharField( max_length=30, blank=True, null=True)  # Field name made lowercase.
    buysource = models.CharField( max_length=250, blank=True, null=True)  # Field name made lowercase.
    org_unit_price = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,)
    org_total_price = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,)
    dinar_unit_price = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,)
    dinar_total_price = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,)
    cost_unit_price = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,)
    cost_total_price = models.DecimalField( blank=True, null=True,max_digits=19, decimal_places=4,)
    note = models.CharField( max_length=200, blank=True, null=True)  
    barcodeno = models.CharField( max_length=25, blank=True, null=True) 
    e_name = models.CharField( max_length=50, blank=True, null=True) 
    prev_quantity = models.IntegerField(null=True,blank=True)
    prev_cost_price = models.DecimalField( max_digits=19, decimal_places=4, blank=True, null=True)
    prev_buy_price = models.DecimalField( max_digits=19, decimal_places=4, blank=True, null=True)
    prev_less_price = models.DecimalField( max_digits=19, decimal_places=4, blank=True, null=True)
    current_quantity = models.IntegerField(null=True,blank=True)
    current_cost_price = models.DecimalField( max_digits=19, decimal_places=4, blank=True, null=True)
    current_buy_price = models.DecimalField( max_digits=19, decimal_places=4, blank=True, null=True)
    current_less_price = models.DecimalField( max_digits=19, decimal_places=4, blank=True, null=True)


    class Meta:
        managed = True
        db_table = 'buy_invoice_items_table'

class StorageTransactions(models.Model):
    storageid = models.AutoField( primary_key=True)  
    account_type = models.CharField( blank=True,max_length=100, null=True) 
    transaction = models.CharField( blank=True,max_length=100, null=True) 
    transaction_date = models.DateField( blank=True, null=True) 
    reciept_no = models.CharField( blank=True,max_length=100, null=True) 
    place =models.CharField( blank=True,max_length=100, null=True) 
    section = models.CharField( blank=True,max_length=200, null=True) 
    subsection =models.CharField( blank=True,max_length=200, null=True) 
    person = models.CharField( blank=True,max_length=200, null=True) 
    amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=4) 
    issued_for = models.CharField( blank=True,max_length=200, null=True) 
    note = models.CharField( blank=True,max_length=200, null=True) 
    payment = models.CharField( blank=True,max_length=200, null=True) 
    daily_status = models.BooleanField( default=True,blank=True) 
    bank = models.CharField( blank=True,max_length=200, null=True) 
    check_no=models.CharField( blank=True,max_length=200, null=True) 
    print_status=models.CharField( blank=True,max_length=50, null=True) 
    done_by=models.CharField( blank=True,max_length=200, null=True) 

    
    class Meta:
        managed = True
        db_table = 'Storage_Transactions_Table'



class AllClientsTable(models.Model):
    clientid = models.AutoField( primary_key=True)  
    name = models.CharField( blank=True,max_length=200, null=True) 
    address = models.CharField( blank=True,max_length=200, null=True) 
    email = models.CharField( blank=True,max_length=200, null=True) 
    website = models.CharField( blank=True,max_length=200, null=True) 
    phone = models.CharField( blank=True,max_length=50, null=True) 
    mobile = models.CharField( blank=True,max_length=50, null=True) 
    last_transaction_details = models.CharField( blank=True,max_length=200, null=True) 
    last_transaction_amount = models.DecimalField( blank=True, null=True, max_digits=19, decimal_places=4) 
    last_transaction = models.DateField( blank=True, null=True)
    accountcurr = models.CharField( blank=True,max_length=50, null=True) 
    type = models.CharField( blank=True,max_length=50, null=True) 
    category = models.CharField( blank=True,max_length=50, null=True) 
    loan_period = models.IntegerField(blank=True, null=True)
    loan_limit = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=4)
    loan_day = models.CharField( blank=True,max_length=50, null=True) 
    subtype = models.CharField( blank=True,max_length=50, null=True) 
    client_stop = models.BooleanField(default=0,null=True,blank=True)
    curr_flag = models.BooleanField(default=0,null=True,blank=True)
    permissions = models.CharField( blank=True,max_length=400, null=True) 
    other = models.CharField( blank=True,max_length=400, null=True) 
    

    class Meta:
        managed = True
        db_table = 'All_Clients_Table'


class AllSourcesTable(models.Model):
    clientid = models.AutoField( primary_key=True)  
    name = models.CharField( blank=True,max_length=200, null=True) 
    address = models.CharField( blank=True,max_length=200, null=True) 
    email = models.CharField( blank=True,max_length=200, null=True) 
    website = models.CharField( blank=True,max_length=200, null=True) 
    phone = models.CharField( blank=True,max_length=50, null=True) 
    mobile = models.CharField( blank=True,max_length=50, null=True) 
    last_transaction_details = models.CharField( blank=True,max_length=200, null=True) 
    last_transaction_amount = models.DecimalField( blank=True, null=True, max_digits=19, decimal_places=4) 
    last_transaction = models.DateField( blank=True, null=True)
    accountcurr = models.CharField( blank=True,max_length=50, null=True) 
    type = models.CharField( blank=True,max_length=50, null=True) 
    category = models.CharField( blank=True,max_length=50, null=True) 
    loan_period = models.IntegerField(blank=True, null=True)
    loan_limit = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=4)
    loan_day = models.CharField( blank=True,max_length=50, null=True) 
    subtype = models.CharField( blank=True,max_length=50, null=True) 
    client_stop = models.BooleanField(default=0,null=True,blank=True)
    curr_flag = models.BooleanField(default=0,null=True,blank=True)
    permissions = models.CharField( blank=True,max_length=400, null=True) 
    other = models.CharField( blank=True,max_length=400, null=True) 
    

    class Meta:
        managed = True
        db_table = 'All_Sources_Table'


class BalanceAndTransactions(models.Model):
    autoid = models.AutoField( primary_key=True)  
    transaction = models.CharField( blank=True,max_length=200, null=True) 
    debt = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=4)
    credit = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=4)
    details = models.CharField( blank=True,max_length=400, null=True) 
    registration_date = models.DateTimeField(db_column='registration_date', blank=True, null=True) 
    delivered_date = models.DateTimeField(db_column='delivered_date', blank=True, null=True)
    delivered_for = models.CharField( blank=True,max_length=150, null=True) 
    current_balance =  models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=4)
    client_id = models.ForeignKey(AllClientsTable, on_delete=models.DO_NOTHING) 
    
    

    class Meta:
        managed = True
        db_table = 'transactions_history_Table'        

class cost_types(models.Model):
    autoid = models.AutoField( primary_key=True)  
    cost_for = models.CharField( blank=True,max_length=200, null=True) 
    class Meta:
        managed = True
        db_table = 'cost_types_Table'

class buyInvoice_costs(models.Model):
    autoid = models.AutoField( primary_key=True)  
    cost_for = models.CharField( blank=True,max_length=200, null=True) 
    cost_price = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=4)
    exchange_rate = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=4)
    dinar_cost_price = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=4)
    invoice = models.ForeignKey(BuyInvoiceTable, on_delete=models.DO_NOTHING) 
    invoice_no = models.IntegerField( blank=True, null=True) 
    
    

    class Meta:
        managed = True

class Ttable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    tname = models.CharField(db_column='TName', max_length=25, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TTable'

class clientTypes(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    tname = models.CharField(db_column='TName', max_length=25, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'clientTypesTable'

class Tablerights(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TableRights'


class Titletable(models.Model):
    fileid = models.BigAutoField(db_column='Fileid', primary_key=True)  # Field name made lowercase.
    titlename = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TitleTable'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

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
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
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


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Maintypetable(models.Model):
    fileid = models.BigAutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    typename = models.CharField(db_column='TypeName', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'mainTypeTable'


class Manufaccountrytable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    countryname = models.CharField(db_column='countryName', max_length=25, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'manufacCountryTable'


class Measurement(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'measurements'


class Modeltable(models.Model):
    fileid = models.AutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    sname = models.CharField(db_column='SName', max_length=25, blank=True, null=True)  # Field name made lowercase.
    maintype = models.ForeignKey(Maintypetable, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'modelTable'


class Productnametable(models.Model):
    fileid = models.BigAutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    typename = models.CharField(db_column='TypeName', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'productNameTable'


class Subtypetable(models.Model):
    fileid = models.BigAutoField(db_column='FileId', primary_key=True)  # Field name made lowercase.
    subtypename = models.CharField(db_column='SubTypeName', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'subTypeTable'
