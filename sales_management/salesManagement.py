try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import *
    from tkinter.ttk import *
    import sqlite3
    from csv import *
    from datetime import datetime, date
    from tkcalendar import Calendar, DateEntry
except:
    import Tkinter as tk
#from tkcalendar import *
#import jinja2
# import os, sys
# from docxtpl import DocxTemplate
# from docx import Document

#Establish DB connection
try:
    conn = sqlite3.connect('C:\\Users\\Admin\\Desktop\\pythonproject\\myfirstdb.db')
except:
    print("DB connection failed")

itemid = ""
stock = 0
grand_total = 0.0
sub_total =0.0
threshold_amount = 0.0
voucher_amount = 0.0
qty = 0
# radio_var = ""
action = ""
tab_no = 0


## Current date
def currentDate():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    return date_str

## Current date and time
def currentDateTime():
    now = datetime.now()
    datetime_str = now.strftime("%Y-%m-%d %H%M%S")
    return datetime_str

#List all item
def showAllItems(tv):
    tv.delete(*tv.get_children())
    cur = conn.cursor()
    sql = 'SELECT * FROM items'
    results = cur.execute(sql)
    #Enter values into tree view 1
    for r in results:
        tv.insert('', 'end', values=r)

#Show all customer
def showCustomers():
    cur = conn.cursor()
    if (tab_no == 0):
        dispCust_trv.delete(*dispCust_trv.get_children())
        sql = 'SELECT firstname, lastname, id FROM customers'
        try:
            results = cur.execute(sql).fetchall()
        except Exception as error:
            print(error)
            return
        #Enter record into tree view
        for r in results:
            dispCust_trv.insert('', 'end', values=r)
    elif(tab_no == 2):
        custInfo_trv.delete(*custInfo_trv.get_children())
        sql = 'SELECT * FROM customers'
        try:
            results = cur.execute(sql).fetchall()
        except Exception as error:
            print(error)
            return
        #Enter values into customer tree view
        for r in results:
            custInfo_trv.insert('', 'end', values=r)
    else:
        return

#Selecting one or multiple item(s) from invoice list for deletion
def deleteInvoiceItems():
    if invoiceItems_trv.selection():
        ls = []
        siid = invoiceItems_trv.selection()
        for dc in siid:
            itId = invoiceItems_trv.item(dc)['values'][0]
            itQty = invoiceItems_trv.item(dc)['values'][3]
            itTotal = invoiceItems_trv.item(dc)['values'][4]
            ls.append(float(itTotal))
            cur = conn.cursor()
            st = 'SELECT stock FROM items WHERE id="'+itId+'"'
            try:
                res = cur.execute(st).fetchone()
            except Exception as error:
                print(error)
                return
            currentStock = res[0]
            newStock = currentStock + itQty
            sql = 'UPDATE items SET stock=? WHERE id=?'
            cur = conn.cursor()
            try:
                cur.execute(sql, (newStock, itId))
                conn.commit()
            except Exception as error:
                print(error)
                return
        global grand_total, threshold_amount
        for t in ls:
            grand_total = grand_total - t
        grand_total_var.set("%.2f" % grand_total)
        invoiceItems_trv.delete(*invoiceItems_trv.selection())
        showAllItems(stockList_trv)
    else:
        messagebox.showerror("Error", "No item(s) to remove or no item in the invoice list has been selected. \nPlease select an item.")
        return
    #invoiceItems_trv.selection_remove(*invoiceItems_trv.selection())
    
# Update the stock and refresh tree view after adding an item to the invoice list
def updateStock():
    newStock = stock - qty
    cur = conn.cursor()
    sql = 'UPDATE items SET stock =? WHERE id =?'
    cur.execute(sql, (newStock, itemid))
    conn.commit()
    showAllItems(stockList_trv)

#Merge duplicate items in the invoice list Remove sel.
def mergeDuplicates():
    ls = list()
    i = 0
    siid = invoiceItems_trv.get_children()
    for s in siid:
        id = invoiceItems_trv.item(s)['values'][0]
        ls.append(id)
    for l in ls:
        if (l == itemid):
            i += 1
    if (i > 1):
        q = list()
        t = list()
        dupList = []
        for d in siid:
            itd = invoiceItems_trv.item(d)['values'][0]
            if (itd == itemid):
                desc = invoiceItems_trv.item(d)['values'][1]
                price = invoiceItems_trv.item(d)['values'][2]
                dupList.append(d) #list for duplicates
                q.append(invoiceItems_trv.item(d)['values'][3]) # list for the quantity of the duplicates
                t.append(invoiceItems_trv.item(d)['values'][4]) # list for the sub-totals
        qtt = q[0] + q[1]
        subTotal = float(t[0]) + float(t[1]) # sum of the sub-totals
        for dl in dupList:
            invoiceItems_trv.delete(dl)
        invoiceItems_trv.insert("", 0, values=[itemid, desc, price, qtt, subTotal])
    else:
        return

# Adding item to the invoice list
def addItem():
    global qty, stock, sub_total, grand_total
    if (item_entry.get() != ""):
        item = item_entry.get()
        qty = int(quantity_spinbox.get())
        price = float(price_entry.get())
        useDiscount = discount_var.get()
        discountValue = float(discount_spinbox.get())
        if(qty > stock):
            instock = qty - stock
            if stock >= 1:
                messagebox.showinfo("Alert", f"Sorry, out of stock. You can only buy {instock} piece(s) for now.")
                return
            else:
                messagebox.showinfo("Alert", f"Sorry, \"{item}\" is out of stock. Please check later.")
                return

        if (discountValue > 0) and (useDiscount == "NO"):
            msg = messagebox.askyesno("Alert", "Do you want to apply the discount rate?")
            if msg == True:
                useDiscount = "YES"
            else:
                return
        if (useDiscount == "YES") and (discountValue >= 0):     
            price = price - float(price * (discountValue/100))
        sub_total = price * qty
        grand_total = grand_total + sub_total
        grand_total_var.set("%.2f" % grand_total) 
        itemList = [itemid, item, price, qty, sub_total]
        invoiceItems_trv.insert('', 0, values=itemList)
        mergeDuplicates()
        updateStock()
        showAllItems(stockList_trv)
        clearItemEntries()
        search_entry.focus()
        item_var.set("")
    else:
        messagebox.showerror("Error", "Please select the item into the item text field")
        return

#Function to reset the input fields for adding new items in tree view 
def clearItemEntries():
    item_var.set("")
    quantity_spinbox.delete(0, END)
    quantity_spinbox.insert(0, "1")
    price_entry.delete(0, END)
    price_entry.insert(0, "0.0")
    discount_spinbox.delete(0, END)
    discount_spinbox.insert(0, "0.0")

def clearCustomerEntry():
    firstname_entry.delete(0, END)
    lastname_entry.delete(0, END)
    custTitle_combo.delete(0, END)
    address_entry.delete(0, END)
    phone_entry.delete(0, END)
    
#Function to create new invoice
def createNewInvoice():
    if invoiceItems_trv.get_children():
        msg = messagebox.askyesnocancel("Message", 
        "Do you want to save the current invoice?", default=messagebox.CANCEL)
        if (msg == True):
            saveInvoice()
        elif (msg == False):
            clearAllInvoiceEntries()
        else:
            return
    else:
        return
   
#Searh for item
def searchItem(e):
    searchInput = search_entry.get()
    stockList_trv.delete(*stockList_trv.get_children())
    cur = conn.cursor()
    sql = 'SELECT * FROM items WHERE id like "%' + searchInput + '%" OR description like "%'+ searchInput +'%"'
    results = cur.execute(sql).fetchall()
    for r in results:
        stockList_trv.insert('', 'end', values=r)

#Searh for item in stock
def searchStockItem(e):
    searchInput = search_stock_entry.get()
    stock_trv.delete(*stock_trv.get_children())
    cur = conn.cursor()
    sql = 'SELECT * FROM items WHERE id like "%'+searchInput+'%" OR description like "%'+searchInput+'%"'
    results = cur.execute(sql).fetchall()
    for r in results:
        stock_trv.insert('', 'end', values=r)

# Clear customer details entry
def clearCEntry():
    global scid
    cFname_entry.delete(0, END)
    cLname_entry.delete(0, END)
    cTitle_combobox.delete(0, END)
    cAddress_entry.delete(0, END)
    cPhone_entry.delete(0, END)
    scid = ""

##Generate the customer ID
def generateCustomerId(name1, name2):
    pad = "000"
    if name1 != "" and name2 != "":
        prefix = (name1[0] + name2[0]).upper()
    elif name1 != "" and name2 == "":
        prefix = name1[:2].upper()
    elif name1 == "" and name2 != "":
        prefix = name2[:2].upper()
    else:
        return
    cur = conn.cursor()
    try:
        res = cur.execute("SELECT COUNT(*) FROM customers").fetchall()
    except Exception as error:
        print(error)
        messagebox.showerror("Error", "Customer ID generation failed.")
        return
    if res[0][0] >= 9 and res[0][0] < 100:
        pad = "00"
    if res[0][0] >= 99 and res[0][0] < 1000:
        pad = "0"
    id = prefix + pad + str(res[0][0] + 1)
    if res[0][0] >= 1000:
        id = prefix + str(res[0][0] + 1)
    return id


#Add customer function
def addCustomer():    
    sql = "INSERT INTO customers(id, firstname, lastname, title, phone, address) VALUES (?,?,?,?,?,?)"
    cur = conn.cursor()
    if (tab_no == 0):
        fname = firstname_entry.get()
        lname = lastname_entry.get()
        phone = phone_entry.get()
        address = address_entry.get()
        title = custTitle_combo.get()
        id = generateCustomerId(fname, lname)
        if ((fname != "") or (lname !="" )):
            values = (id, fname, lname, title, phone, address)
        else:
            messagebox.showerror("Error", "Please fill in the customer details.")
            return
    elif (tab_no == 2):
        if (scid != ""):
            messagebox.showerror("Error", "This customer already exist. You can only update.")
            return
        else:
            cFname = cFname_entry.get()
            cLname = cLname_entry.get() 
            cTitle = cTitle_combobox.get()
            cPhone = cPhone_entry.get()
            cAddress = cAddress_entry.get()
            id = generateCustomerId(cFname, cLname)
            if ((cFname != "") or (cLname != "")):
                values = (id, cFname, cLname, cTitle, cPhone, cAddress)
            else:
                messagebox.showerror("Error", "Firstname or lastname field is empty. Please check.")
                return
    else:
        return
    try:
        cur.execute(sql, values)
        conn.commit()
    except Exception as error:
        print(error)
        messagebox.showerror("Error", "Operation failed. The customer could not be added.")
        return
    clearCEntry()
    showCustomers()
    messagebox.showinfo("Message", "Customer successfully added.")

#Delete customer from the customer list
def deleteCustomer():
    siid = custInfo_trv.selection()
    cur = conn.cursor()
    if (len(siid) > 0):
        for s in siid:
            custId = str(custInfo_trv.item(s)['values'][0])
            custFName = custInfo_trv.item(s)['values'][1]
            custLName = custInfo_trv.item(s)['values'][2]
            st = 'DELETE FROM customers WHERE id="'+custId+'"'
            if (messagebox.askyesno("Message", f"Are you sure you want to delete customer \"{custFName} {custLName}\" ?")):
                try:
                    cur.execute(st)
                except:
                    messagebox.showerror("Error", "Delete operation failed. Something went wrong.")
            else:
                return
        conn.commit()
        custInfo_trv.delete(*custInfo_trv.selection())
        showCustomers()
    else:
        messagebox.showerror("Error", "Select customer from the list to delete.")
        return

#Search customer
def searchCustomer(e):
    cur = conn.cursor()
    #Search customer name in onvoice page
    if(tab_no == 0):
        searchInput = searchCust_entry.get()
        dispCust_trv.delete(*dispCust_trv.get_children())
        cur = conn.cursor()
        sql = 'SELECT firstname, lastname, id FROM customers WHERE id like "%'+ searchInput +'%" OR firstname like "%'+ searchInput +'%" OR lastname like "%'+ searchInput +'%" OR address like "%'+ searchInput +'%"'
        results = cur.execute(sql)
        for r in results:
            dispCust_trv.insert('', 'end', values=r)
    #Search customer name in manage customer page bind
    elif(tab_no == 2):
        searchInput = search_customer_entry.get()
        custInfo_trv.delete(*custInfo_trv.get_children())
        sql = 'SELECT * FROM customers WHERE id like "%'+ searchInput +'%" OR firstname like "%'+ searchInput +'%" OR lastname like "%'+ searchInput +'%" OR address like "%'+ searchInput +'%"'
        results = cur.execute(sql)
        for r in results:
            custInfo_trv.insert('', 'end', values=r)
    else:
        return

#Radio button selection
msg = ""
def onSelectRadio():
    global action, msg
    action = radio_var.get()
    if (action == "updateQty"):
        itemId_entry.configure(state="readonly")
        itemName_entry.configure(state="readonly")
        itemPrice_entry.configure(state="readonly")
        itemQty_entry.configure(state="normal")
        updateStock_Btn.configure(text="Add to qty")
        msg = "Quantity update successful."
    elif (action == "updatePrice"):
        itemId_entry.configure(state="readonly")
        itemName_entry.configure(state="readonly")
        itemQty_entry.configure(state="readonly")
        itemPrice_entry.configure(state="normal")
        updateStock_Btn.configure(text="Update price")
        msg = "Price update successful."
    elif (action == "deleteItem"):
        itemName_entry.configure(state="readonly")
        itemQty_entry.configure(state="readonly")
        itemPrice_entry.configure(state="readonly")
        updateStock_Btn.configure(text="Delete Item")
        msg = "Item successfully deleted."
    elif (action == "addNewItem"):
        itemId_entry.configure(state="normal")
        itemName_entry.configure(state="normal")
        itemQty_entry.configure(state="normal")
        itemPrice_entry.configure(state="normal")
        updateStock_Btn.configure(text="Add new item")
        itemId_entry.focus()
        msg = "New item added successfully."
    else:
        return

#Add item to stock
def manageStock():
    itemId = itemId_entry.get().upper()
    itemName = itemName_entry.get()
    itemPrice = itemPrice_entry.get()
    itemQty = itemQty_entry.get()
    newStock = 0
    values = ""
    cur = conn.cursor()
    global action, msg
    if (itemId != ""):
        if (action == "addNewItem"):
            if (itemName != ""):
                if (float(itemPrice.isdigit()) and int(itemQty.isdigit())):
                    newStock = itemQty
                    sql = "INSERT INTO items(id, description, price, stock) VALUES (?,?,?,?)"
                    values = (itemId, itemName, itemPrice, newStock)
                    try:
                        cur.execute(sql, values)
                        clearStockEntry()
                    except:
                        messagebox.showerror("Error", f"Item ID {itemId} already exist. Please check.")
                        return
                else:
                    messagebox.showerror("Error", 
                                         "You did not enter correct number for price or quantity. Please check.")
                    return
            else:
                messagebox.showwarning("Alert", "Pleas enter name of the item.")
                return
        elif (action == "updateQty"):
            qr = 'SELECT stock FROM items WHERE id="'+itemId+'"'
            res = cur.execute(qr).fetchone()
            stk = res[0]
            if ((itemQty.isdigit())):
                newStock = int(stk) + int(itemQty)
                sql = 'UPDATE items SET stock =? WHERE id =?'
                try:
                    cur.execute(sql, (newStock, itemId))
                except:
                    messagebox.showerror("Error", "The update operation failed!")
                    return
                clearStockEntry()
            else:
                messagebox.showerror("Error", "You entered a wrong number. Pleace check.")
                return
        elif (action == "updatePrice"):
            if (float(itemPrice.isdigit())): 
                sql = 'UPDATE items SET price =? WHERE id =?'
                if (messagebox.askyesno("Alert", f"Do you really want to change the price to {itemPrice}?")):
                    try:
                        cur.execute(sql, (itemPrice, itemId))
                    except Exception as error:
                        print(f"Error: {error}")
                        messagebox.showerror("Error", "The update operation failed!")
                        return
                else:
                    return
            else:
                messagebox.showerror("Error", "You did not enter correct number. Pleace check.")
                return
        elif(action == "deleteItem"):
            sql = 'DELETE FROM items WHERE id="'+itemId+'"'
            if (itemId != ""):
                if (messagebox.askyesno("Alert", "Do you really want to remove this item from stock?")): 
                    try:
                        cur.execute(sql)
                    except Exception as error:
                        print(f"Error: {error}")
                        messagebox.showerror("Error", "The delete operation failed!")
                        return
                else:
                    return
            else:
                messagebox.showerror("Error", "Item not found. Please check the item ID")
                return  
        else:
            messagebox.showerror("Error", "Something went wrong. Try again")
            return
        conn.commit()
        clearStockEntry()
        showAllItems(stock_trv)
        messagebox.showinfo("Message", msg)
    else:
        messagebox.showerror("Error", "Please enter the item ID.")
        return

#Remove selected item and update db
def clearSelectedItem():
    if item_entry.get() != "":
        clearItemEntries()
    else:
        return

#Verify voucher code against customer id
def checkVoucherCode():
    global threshold_amount
    voucher = voucher_entry.get()
    if (voucher != ""):
        cur = conn.cursor()
        qr = 'SELECT code, amount, threshold FROM voucher WHERE code=(SELECT vcode FROM customers WHERE vcode="'+voucher+'")'
        res = cur.execute(qr).fetchone()
        voucher_code = res[0]
        voucher_amount = res[1]
        threshold_amount = res[2]
    else:
        return

#Calculatate voucher amount and redeem
def redeemVoucher():
    checkVoucherCode()
    global grand_total, voucher_amount
    if (voucher_entry.get() != ""):
        if (grand_total >= (2 * threshold_amount)):
            print(grand_total, threshold_amount)
            answer = messagebox.askyesnocancel("Message", 
                                        f"Once redeemed, it cannot be re-used. Your total purchase must be at least GHS{2 * threshold_amount}. Do you really want to redeem the voucher?",
                                        default=messagebox.CANCEL)
            if (answer == True):
                voucher_amount = threshold_amount
                # *** implement deleteUsedVoucher() from db later
                voucher_entry.configure(state="readonly")
                messagebox.showinfo("Message", 
                                f"Voucher verified. GHS{threshold_amount} will be deducted from the total purchase.")
            elif (answer == False):
                voucher_entry.delete(0, END)
                return
            else:
                return
        else:
            messagebox.showinfo("Information", f"Your total purchase must be at least GHS{2 * threshold_amount} before voucher can be applied.")
            return
    else:
        messagebox.showwarning("Message","Please enter the voucher code.")
        return

#Clear all invoicesentries
def clearAllInvoiceEntries():
    global grand_total
    grand_total = 0.0
    grand_total_var.set(grand_total)
    voucher_entry.delete(0, END)
    discount_var.set("NO")
    voucherState_var.set("NO")
    invoiceItems_trv.delete(*invoiceItems_trv.get_children())
    clearItemEntries()
    clearCustomerEntry()

## Highlight tree view row
def highlightRow(event):
    trv = event.widget
    row = trv.identify_row(event.y)
    trv.tk.call(trv, "tag", "remove", "highlight")
    trv.tk.call(trv, "tag", "add", "highlight", row)

## Binding highlightRow() to tree view row
def highlight_row(trv):
    trv.tag_configure("highlight", background="lightblue")
    trv.bind('<Motion>', highlightRow)

## Remove the highlight when the mouse leaves the widget
def removeHighlight(event):
    trv = event.widget
    trv.tk.call(trv, "tag", "remove", "highlight")

## Binding remove the highlight when the mouse leaves the widget
def removeHighlight_row(trv):
    trv.tag_configure("highlight", background="lightblue")
    trv.bind('<Leave>', removeHighlight)


##Display all sales tree view
def showAllSales():
    ls = []
    cur = conn.cursor()
    qr = 'SELECT i.id, i.description, i.price, s.qty, s.total, s.date FROM items i INNER  JOIN sales s ON  i.id=s.id ORDER BY s.date'
    res = cur.execute(qr).fetchall()
    sales_trv.delete(*sales_trv.get_children())
    for r in res:
        sales_trv.insert("", 0, values=r)

## Get the total sales
def getTotalSales():
    qty_list = []
    total_sales_list = []
    totalQty = 0
    totalSales = 0.0
    sales = sales_trv.get_children()
    for s in sales:
        qty = sales_trv.item(s)["values"][3]
        qty_list.append(qty)
        total = sales_trv.item(s)["values"][4]
        total_sales_list.append(total)
    for q in qty_list:
        totalQty = totalQty + int(q)
    totalQty_var.set(totalQty)
    for t in total_sales_list:
        totalSales = totalSales + float(t)
    totalSales_var.set(totalSales)

##
def checkStartDateFormat(sDate):
    sDate = sDate
    if sDate != "":
        if (sDate[0:4].isdigit() and sDate[5:7].isdigit() and sDate[8:10]): #2023-04-13
            if sDate[4] == "-" and sDate[7] == "-":
                return True
            else:
                messagebox.showerror("Error", "The date format you entered is not correct.\nUse \"-\" as separater.")
                return False
        else:
            messagebox.showerror("Error", "The date format you entered is not correct.\nCheck and enter digits where appropriate.")
            return False
##
def checkEndDateFormat(tDate):
    tDate = tDate
    if(tDate != ""):
        if (tDate[0:4].isdigit() and tDate[5:7].isdigit() and tDate[8:10]): #2023-04-13
            if tDate[4] == "-" and tDate[7] == "-":
                return True
            else:
                messagebox.showerror("Error", "The date format you entered is not correct.\nUse \"-\" as separater.")
                return False
        else:
            messagebox.showerror("Error", "The date format you entered is not correct.\nCheck and enter digits where appropriate.")
            return False
    else:
        return True
        
##Filter and Display all sales in tree view
def filterAllItemSales():
    startDate = fromEntry.get()
    endDate = toEntry.get()
    cur = conn.cursor()
    if ((startDate != "") and (endDate != "")):
        if (endDate >= startDate):
            qr = 'SELECT i.id, i.description, i.price, s.qty, s.total, s.date FROM items i INNER  JOIN sales s ON  i.id=s.id WHERE s.date BETWEEN "'+startDate+'" AND "'+endDate+'"'
        else:
            messagebox.showerror("Error", "The \"end date\" must be greater than the \"start date\".")
            return
    elif ((startDate != "") and (endDate == "")):
        qr = 'SELECT i.id, i.description, i.price, s.qty, s.total, s.date FROM items i INNER  JOIN sales s ON  i.id=s.id WHERE s.date >= "'+startDate+'"'
    elif ((startDate == "") and (endDate != "")):
        qr = 'SELECT i.id, i.description, i.price, s.qty, s.total, s.date FROM items i INNER  JOIN sales s ON  i.id=s.id WHERE s.date <= "'+endDate+'"'
    elif ((startDate == "") and (endDate == "")):
       qr = 'SELECT i.id, i.description, i.price, s.qty, s.total, s.date FROM items i INNER  JOIN sales s ON  i.id=s.id ORDER BY s.date'
    try:
        res = cur.execute(qr).fetchall()
        if res == []:
            messagebox.showinfo("Message", "There are no records for this search criteria.")
            return
    except:
        messagebox.showerror("Error", "Could not fetch the records. Please check the date format entered.")
        return
    sales_trv.delete(*sales_trv.get_children())
    for r in res:
        sales_trv.insert("", 0, values=r)
    getTotalSales()

##Filter specific item sales and Display in tree view
def filterSpecificItemSales():
    id = itemIdCombo.get()
    startDate = fromEntry.get()
    endDate = toEntry.get()
    cur = conn.cursor()
    if id != "":
        if ((startDate != "") and (endDate != "")): 
            if (endDate >= startDate):
                qr = 'SELECT i.id, i.description, i.price, s.qty, s.total, s.date FROM items i INNER  JOIN sales s ON  i.id=s.id WHERE i.id="'+id+'" AND s.date BETWEEN "'+startDate+'" AND "'+endDate+'"'
            else:
                messagebox.showerror("Error", "The \"end date\" must be greater than the \"start date\".")
                return
        elif ((startDate != "") and (endDate == "")):
            qr = 'SELECT i.id, i.description, i.price, s.qty, s.total, s.date FROM items i INNER  JOIN sales s ON  i.id=s.id WHERE i.id="'+id+'" AND s.date >= "'+startDate+'"'
        elif ((startDate == "") and (endDate != "")):
            qr = 'SELECT i.id, i.description, i.price, s.qty, s.total, s.date FROM items i INNER  JOIN sales s ON  i.id=s.id WHERE i.id="'+id+'" AND s.date <= "'+endDate+'"'
        elif ((startDate == "") and (endDate == "")):
            qr = 'SELECT i.id, i.description, i.price, s.qty, s.total, s.date FROM items i INNER  JOIN sales s ON  i.id=s.id WHERE i.id="'+id+'" ORDER BY s.date'
        try:
            res = cur.execute(qr).fetchall()
            if res == []:
                sales_trv.delete(*sales_trv.get_children())
                messagebox.showinfo("Message", "There are no records for this search criteria.")
                showAllSales()
                return
        except:
            messagebox.showerror("Error", "Could not fetch the records. Please check the date format entered.")
            return
        sales_trv.delete(*sales_trv.get_children())
        for r in res:
            sales_trv.insert("", 0, values=r)
        getTotalSales()
    else:
        messagebox.showerror("Error", "Please select or enter the item ID.")
        return
    
## filter sales records
def filterSales():
    if (sradio_var.get() == "allItems"):
        filterAllItemSales()
    elif(sradio_var.get() == "specificItem"):
        filterSpecificItemSales()


## Insert new record into sales
def insertNewIntoSales(item, cur, query):
    values = (item[0], item[3], item[4], currentDate())
    try:
        cur.execute(query, values)
    except Exception as error:
        print(f"Error: {error}")
        messagebox.showerror("Error", "Updating sales records faild!")
        return
    conn.commit()

## Update sales records
def updateSalesRecords(list):
    cur = conn.cursor()
    qr1 = 'INSERT INTO sales (id, qty, total, date) VALUES (?,?,?,?)'
    qr2 = 'UPDATE sales SET qty=?, total=? WHERE id=? and date=?'
    for item in list:
        id = item[0]
        res = cur.execute('SELECT id, qty, total, date FROM sales WHERE id="'+id+'"').fetchall()
        if (res == []):
            insertNewIntoSales(item, cur, qr1)
        elif (res != []):
            lst = []
            for r in res:
                lst.append(r[3])
                lst.sort()
            if (lst[len(lst) - 1] < currentDate()):
                insertNewIntoSales(item, cur, qr1)
            elif (lst[len(lst) - 1] == currentDate()):
                qty = int(item[3]) + int(res[len(res) - 1][1])
                total = float(item[4]) + float(res[len(res) - 1][2])
                try:
                    cur.execute(qr2, (qty, total, id, currentDate()))
                except Exception as error:
                    print(f"Error: {error}")
                    messagebox.showerror("Error", "Updating sales records faild!")
                    return
            else:
                return
            lst.clear()
    conn.commit()
    showAllSales()

#Get the invoice data
def getInvoiceData():
    global grand_total, voucher_amount, invoice_amount
    invoiceList = []
    sid = invoiceItems_trv.get_children()
    if (voucher_amount > 0):
        invoice_amount = grand_total - voucher_amount
    else:
        invoice_amount = grand_total
    for s in sid:
        id = invoiceItems_trv.item(s)['values'][0]
        item = invoiceItems_trv.item(s)['values'][1]
        price = invoiceItems_trv.item(s)['values'][2]
        qty = invoiceItems_trv.item(s)['values'][3]
        total = invoiceItems_trv.item(s)['values'][4]
        header = ["ID", "Item", "Price", "Qty", "Total"]
        invoiceList.append([id, item, price, str(qty), total])
    
    global voucher_discount, invoice_total, g_total

    g_total = ["Grand total", grand_total]
    voucher_discount = ["Voucher discount", voucher_amount]
    invoice_total = ["Invoice Total", invoice_amount]
    writeInvoiceToFile(header, invoiceList)
    updateSalesRecords(invoiceList)
    voucher_discount.clear()

#write invoice to file 
def writeInvoiceToFile(header, list):
    global voucher_discount, g_total
    fname = firstname_entry.get()
    lname = lastname_entry.get()
    if fname != "" and lname != "":        
        path = f"C:\\Users\\Admin\\Desktop\\pythonproject\\invoice\\invoice_{fname}_{lname}_{currentDateTime()}.csv"
    elif fname == "" and lname != "":
        path = f"C:\\Users\\Admin\\Desktop\\pythonproject\\invoice\\invoice_{lname}_{currentDateTime()}.csv"
    elif fname != "" and lname == "":
        path = f"C:\\Users\\Admin\\Desktop\\pythonproject\\invoice\\invoice_{fname}_{currentDateTime()}.csv"
    elif fname == "" and lname == "":
        messagebox.showerror("Error", "Could not generate the invoice.\nPlease enter the cutomer name for this invoice.")
        return   
    try:
        with open(path, "w", newline='') as file:
            fw = writer(file, delimiter=',')
            fw.writerow(header)
            for b in list:
                fw.writerow(b)
            fw.writerow(g_total)
            fw.writerow(voucher_discount)
            fw.writerow(invoice_total)
            file.close()
            messagebox.showinfo("Message", "Invoice successfully generated.")
            clearAllInvoiceEntries()
    except Exception as error:
        print(error)
        messagebox.showerror("Error", "Could not generate the invoice!")
        return


# write sales records to file
def exportSalesRecords():
    total_quantity = totalQty_entry.get()
    total_sales = totalSales_entry.get()
    salesList = []
    sid = sales_trv.get_children()
    for s in sid:
        id = sales_trv.item(s)['values'][0]
        item = sales_trv.item(s)['values'][1]
        price = sales_trv.item(s)['values'][2]
        qty = sales_trv.item(s)['values'][3]
        total = sales_trv.item(s)['values'][4]
        sdate = sales_trv.item(s)['values'][5]
        header = ["ID", "Item", "Unit price", "Qty", "Total", "Date"]
        salesList.append([id, item, price, str(qty), total, sdate])
        tq = ["Total qty", total_quantity]
        ts = ["Total sales", total_sales]
        path = f"C:\\Users\\Admin\\Desktop\\pythonproject\\sales\\sales_{currentDateTime()}.csv"
    try:
        with open(path, "w", newline='') as file:
            fw = writer(file, delimiter=',')
            fw.writerow(header)
            for s in salesList:
                fw.writerow(s)
            fw.writerow(tq)
            fw.writerow(ts)
            file.close()
            messagebox.showinfo("Message", "Sales records successfully exported.")
    except Exception as error:
        print(error)
        messagebox.showerror("Error", "The record(s) export failed!")


## Select customer for invoice 
scid = ""
def selectCustomer(e):
    global scid
    cur = conn.cursor()
    if (tab_no == 0):
        if dispCust_trv.selection():
            sid = dispCust_trv.selection()  
            id = str(dispCust_trv.item(sid)['values'][2])
            try:
                res = cur.execute('SELECT * FROM customers WHERE id="'+id+'"').fetchone()
                clearCustomerEntry()
                fname_var.set(res[1])
                lname_var.set(res[2])
                phone_var.set(res[3])
                address_var.set(res[4])
                title_var.set(res[5])
            except Exception as error:
                print(error)
            dispCust_trv.selection_remove(dispCust_trv.selection())
    elif (tab_no == 2):
        if custInfo_trv.selection():
            sid = custInfo_trv.selection()
            id = str(custInfo_trv.item(sid)['values'][0])
            scid = id
            try:
                res = cur.execute('SELECT * FROM customers WHERE id="'+id+'"').fetchone()
                clearCustomerEntry()
                cFname_var.set(res[1])
                cLname_var.set(res[2])
                cPhone_var.set(res[3])
                cAddress_var.set(res[4])
                cTitle_var.set(res[5])
            except Exception as error:
                print(error)
            custInfo_trv.selection_remove(custInfo_trv.selection())
    else:
        messagebox.showerror("Error", "Please, first select customer from the list.")
        return

## Focus and highlight an entry widget
def focusAndHighlight(wgt):
    wgt.focus()
    wgt.selection_range(0, END)

## Select item for update in stock management
def selectItemForUpdate(e):
    cur = conn.cursor()
    if stock_trv.selection():
        sid = stock_trv.selection()
        id = str(stock_trv.item(sid)['values'][0])
        try:
            rs = cur.execute('SELECT * FROM items WHERE id="'+id+'"').fetchone()
        except Exception as error:
            print("Error:", error)
        itemId_var.set(rs[0])
        itemName_var.set(rs[1])
        itemPrice_var.set(rs[2])
        itemQty_var.set(rs[3])
        if (action == "updateQty"):
            focusAndHighlight(itemQty_entry)
        elif (action == "updatePrice"):
            focusAndHighlight(itemPrice_entry)
        else:
            focusAndHighlight(itemId_entry)
        stock_trv.selection_remove(stock_trv.selection())
    else:
        messagebox.showerror("Error", "Please, first select an item from the stock list.")
        return

## clear stock entry
def clearStockEntry():
    itemId_entry.delete(0, END)
    itemName_entry.delete(0, END)
    itemPrice_entry.delete(0, END)
    itemQty_entry.delete(0, END)
    itemId_var.set("")
    itemName_var.set("")
    itemPrice_var.set("")
    itemQty_var.set("")

## Update customer information in manage customer
def updateCustomerInfo():
    global scid
    fname = cFname_entry.get()
    lname = cLname_entry.get()
    phone = cPhone_entry.get()
    address = cAddress_entry.get()
    title = cTitle_combobox.get()
    sql = 'UPDATE customers SET firstname=?, lastname=?, phone=?, address=?, title=? WHERE id="'+scid+'"'
    values = (fname, lname, phone, address, title)
    cur = conn.cursor()
    if ((fname != "") or (lname !="") and scid != ""):
        try:
            cur.execute(sql, values)
            conn.commit()
        except Exception as error:
            print(error)
            messagebox.showerror("Error", "Update failed. Try again.")
            return
        showCustomers()
        clearCEntry()
        messagebox.showinfo("Message", "Update is successful.")
    else:
        messagebox.showwarning("Warning", "Please select from the customer list.")
        return

## Select item from stock list
def selectItem(e):
    global itemid, stock
    if stockList_trv.selection():
        selectedItem = stockList_trv.selection()
        itemid = stockList_trv.item(selectedItem)['values'][0]
        itemName = stockList_trv.item(selectedItem)['values'][1]
        unitPrice = stockList_trv.item(selectedItem)['values'][2]
        stock = stockList_trv.item(selectedItem)['values'][3]
        item_var.set(itemName)
        price_var.set(unitPrice)
        quantity_spinbox.focus()
        quantity_spinbox.selection_range(0, END)
    else:
        messagebox.showwarning("Message", "Please click on the item in the stock list first.")
        return

## DoubleClick to Select specific item from stock list in sales tab for filter
def selectItemInSearchSales(e):
    sItem = search_trv.selection()
    itemid = search_trv.item(sItem)['values'][0]
    itemName = search_trv.item(sItem)['values'][1]
    if sradio_var.get() == "specificItem":
        c.set(itemid)
        n.set(itemName)
    else:
        messagebox.showwarning("Alert", "Please select the \"Specific item\" radio button first.")
        return

#Save invoice 
def saveInvoice():
    getInvoiceData()
    voucher_entry.configure(state="normal")

#Check before save
def checkAndSave():
    if invoiceItems_trv.get_children():
        if (item_entry.get() != ""):
            answer = messagebox.askyesnocancel(
                "Message", 
                "You still have 1 item selected but not added to the invoice list. Do you want to add it?")
            if (answer == True):
                addItem()
                saveInvoice()
            elif (answer == False):
                clearItemEntries()
                saveInvoice()
            else:
                return
        else:
            saveInvoice()
    else:
        messagebox.showerror("Error", "No invoice data to save.")
        return

def getTabIndex(*args):
    global tab_no
    tab_no = notebook.index(notebook.select())
    showCustomers()

##Filling sales item id combo
def fillItemIdCombo():
    cur = conn.cursor()
    try:
        res = cur.execute("SELECT id FROM items").fetchall()
    except Exception as error:
        print(error)
        return
    values = []
    for r in res:
        values.append(r)
    values = tuple(values)
    return values

##Filling sales item name combo
def fillItemNameCombo():
    cur = conn.cursor()
    try:
        res = cur.execute("SELECT description FROM items ORDER BY description").fetchall()
    except Exception as error:
        print(error)
        return
    values = []
    for r in res:
        values.append(r)
    values = tuple(values)
    return values

## search item by id in sales
def searchNameById(e):
    id = itemIdCombo.get()
    cur = conn.cursor()
    qr = 'SELECT description FROM items WHERE id="'+id+'"'
    if (id != ""):
        try:
            res = cur.execute(qr).fetchone()
        except Exception as error:
            print(error)
            messagebox.showerror("Error", "Could not find an item that matches this ID.")
            return
        itemNameCombo.delete(0, END)
        n.set(res[0])
    
## search item by name in sales
def searchIdByName(e):
    name = itemNameCombo.get()
    cur = conn.cursor()
    qr = 'SELECT id FROM items WHERE description="'+name+'"'
    if (name != ""):
        try:
            res = cur.execute(qr).fetchone()
        except Exception as error:
            print(error)
            messagebox.showerror("Error", "Could not find an ID that matches this item.")
            return
        itemIdCombo.delete(0, END)
        c.set(res[0])
    else:
        return

## search a specific item in and select it for filter in sales
def searchList(e):
    searchInput = searchSales_entry.get()
    cur = conn.cursor()
    qr = 'SELECT id, description FROM items WHERE id like "%'+searchInput+'%" OR description like "%'+searchInput+'%"'
    try:
        res = cur.execute(qr).fetchall()
    except Exception as error:
        print(error)
        return
    search_trv.delete(*search_trv.get_children())
    for r in res:
        search_trv.insert("", 0, values=r)
    else:
        return

## Radio button selection for sales filter options
def onSelectSalesRadio():
    option = sradio_var.get()
    if (option == "allItems"):
        itemIdCombo.delete(0, END)
        itemNameCombo.delete(0, END)
        itemIdCombo.configure(state="readonly")
        itemNameCombo.configure(state="readonly")
        itemIdCombo['values'] = ""
        itemNameCombo['values'] = ""
        showAllSales()
    elif (option == "specificItem"):
        itemIdCombo.configure(state="normal")
        itemNameCombo.configure(state="normal")
        itemIdCombo['values'] = (fillItemIdCombo())
        itemNameCombo['values'] = (fillItemNameCombo())

## Insert stock items or list in sales
def showItemsInSales():
    cur = conn.cursor()
    try:
        res = cur.execute('SELECT id, description FROM items').fetchall()
    except Exception as error:
        print("Could not load the records.")
        print(f"Error: {error}")
        return
    for r in res:
        search_trv.insert("", 0, values=r)

#Edit invoice
def editInvoice():
    print("Yet to implement this function.\nPlease check later.")

#Setting window position
def windowPosition():
    w = 1080
    h = 657
    screenWidth = window.winfo_screenwidth()
    screenHeight = window.winfo_screenheight()
    x = (screenWidth - w)/2
    y = (screenHeight - h)/6
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    #print("Window position x and y {0} {1}".format(x, y))

window = tk.Tk()
#window.geometry("1080x650+0+0")
windowPosition()
window.title("Sales Management")

#Fixed-size window
#window.resizable(0, 0)

#mainframe.grid(row=0, column=0, sticky="news", padx=10, pady=10)

## Notebook or tab
notebook = ttk.Notebook(window)
notebook.pack(padx=5, pady=2)

#Frames for the notebook
invoice_tab = tk.Frame()
stock_tab = tk.Frame()
customer_tab = tk.Frame()
sales_tab = tk.Frame()
##Adding frames to the notebook
notebook.add(invoice_tab, text="Invoice")
notebook.add(stock_tab, text="Manage stock")
notebook.add(customer_tab, text="Manage customer")
notebook.add(sales_tab, text="Sales")
notebook.bind('<<NotebookTabChanged>>', getTabIndex)

#Stock list Tree view frame
stockList_trv_frame = tk.LabelFrame(invoice_tab, text="Stock list")
stockList_trv_frame.grid(row=0, column=0, sticky="news", padx=10, pady=2)

#Tree view 1 columns and headers
stockList_trvStyle = ttk.Style()
st = ttk.Style()
st.theme_use('clam')
# Configure the style of Heading in Treeview widget
st.configure('t.Treeview.Heading', background="grey", relief="flat")

#style = ttk.Style()
#stockList_trvStyle.configure("LB.TLabel", foreground="green", background="white")

# Add tree view vertical Scrollbar
stockList_trv_vscroll = ttk.Scrollbar(stockList_trv_frame, orient='vertical')
stockList_trv = ttk.Treeview(stockList_trv_frame, height=8, yscrollcommand=stockList_trv_vscroll.set)
stockList_trv["columns"] = ("id", "desc", "price", "instock")
stockList_trv["show"]="headings"
stockList_trv.column("id", width=30, anchor="c")
stockList_trv.column("desc", width=150, anchor="c")
stockList_trv.column("price", width=30, anchor="c")
stockList_trv.column("instock", width=30, anchor="c")

stockList_trv.heading("id", text="ID")
stockList_trv.heading("desc", text="Description")
stockList_trv.heading("price", text="Unit price")
stockList_trv.heading("instock", text="Qty in stock")
stockList_trv.grid(row=0, column=0,padx=2, pady=4, sticky="news")
stockList_trv.bind('<Double-1>', selectItem)
highlight_row(stockList_trv)
removeHighlight_row(stockList_trv)

#Configure and attach the scrollbar to widget
stockList_trv_vscroll.configure(command=stockList_trv.yview)
stockList_trv_vscroll.grid(row=0, column=1, sticky="news", padx=2, pady=10)

#Search
search_frame = tk.Frame(stockList_trv_frame)
search_frame.grid(row=1, column=0, sticky="news")

search_entry = tk.Entry(search_frame, width=30)
search_entry.grid(row=0, column=0, sticky="news", padx=10, pady=10)
search_entry.bind('<KeyRelease>', searchItem)
search_label = tk.Label(search_frame, text="Search")
search_label.grid(row=0, column=2, sticky="w", padx=2, pady=10)

#Select item from stock button
select_item_btn = tk.Button(search_frame, text="Select", width=15, command=lambda:selectItem(select_item_btn))
select_item_btn.grid(row=0, column=3, sticky="news", padx=20, pady=10)

#Button frame
bottom_group_frame = tk.LabelFrame(invoice_tab)
bottom_group_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=10)

#Customer info frame
custInfo_frame = tk.LabelFrame(bottom_group_frame)
custInfo_frame.grid(row=0, column=8, rowspan=2, sticky="news", padx=10, pady=10)

#First name
fname_var = StringVar()
firstname_label = tk.Label(custInfo_frame, text="First name")
firstname_label.grid(row=0, column=0)
firstname_entry = tk.Entry(custInfo_frame, textvariable=fname_var)
#firstname_entry.bind('<KeyRelease>', searchCustomerName)
firstname_entry.grid(row=1, column=0, sticky="we", padx=2)

#Last name
lname_var = StringVar()
lastname_label = tk.Label(custInfo_frame, text="Last name")
lastname_label.grid(row=0, column=1)
lastname_entry = tk.Entry(custInfo_frame, textvariable=lname_var)
lastname_entry.grid(row=1, column=1)

#Customer name title
title_var = StringVar()
customerTitle_label = tk.Label(custInfo_frame, text="Title")
customerTitle_label.grid(row=2, column=0)
custTitle_combo = ttk.Combobox(custInfo_frame, textvariable=title_var, values=["", "Mr.", "Mrs.", "Ms", "Miss"])
custTitle_combo.grid(row=3, column=0)

#Phone number
phone_var = StringVar()
phone_label = tk.Label(custInfo_frame, text="Phone number")
phone_label.grid(row=2, column=1)
phone_entry = tk.Entry(custInfo_frame, textvariable=phone_var)
phone_entry.grid(row=3, column=1)

#Address
address_var = StringVar()
address_label = tk.Label(custInfo_frame, text="Address")
address_label.grid(row=4, column=0)
address_entry = tk.Entry(custInfo_frame, textvariable=address_var)
address_entry.grid(row=5, column=0, sticky="news", padx=5)

#Wiget spacing
for wgt in custInfo_frame.winfo_children():
    wgt.grid_configure(padx=5, pady=3)

#Save invoice
saveInvoice_button = tk.Button(custInfo_frame, text="Save invoice", command=checkAndSave)
saveInvoice_button.grid(row=6, column=0, padx=5, pady=8, sticky="news")

#Add customer
addCustomer_button = tk.Button(custInfo_frame, text="Add customer", command=addCustomer)
addCustomer_button.grid(row=6, column=1, padx=5, pady=8, sticky="news")

#Clear entry btn
# clearEntry_button = tk.Button(custInfo_frame, text="Clear", command=clearCustomerEntry)
# clearEntry_button.grid(row=6, column=1, padx=5, pady=8, sticky="news")

#Items frame
item_frame = tk.Frame(stockList_trv_frame)
item_frame.grid(row=2, column=0, sticky="news", padx=5, pady=10)

#Item list
item_var = StringVar()
item_label = tk.Label(item_frame, text="Item")
item_label.grid(row=0, column=0)
item_entry = tk.Entry(item_frame, state="readonly", textvariable=item_var, width=25)
item_entry.grid(row=1, column=0)

#Item price
price_var = StringVar(value=0.0)
price_label = tk.Label(item_frame, text="Unit price")
price_label.grid(row=0, column=1)
price_entry = tk.Entry(item_frame, textvariable=price_var, width=15)
price_entry.grid(row=1, column=1)

#Item quantiy
qty_var = tk.StringVar()
quantity_label = tk.Label(item_frame, text="Quantity")
quantity_label.grid(row=0, column=2)
quantity_spinbox = tk.Spinbox(item_frame, textvariable=qty_var, from_=1, to="infinity", width=15)
quantity_spinbox.grid(row=1, column=2)
#quantity_spinbox.bind('<FocusIn>', focusAndHighlight)

#Price dicount
discount_label = tk.Label(item_frame, text="Discount(%)")
discount_label.grid(row=0, column=4)
discount_spinbox = tk.Spinbox(item_frame, from_=0, to=100, width=15)
discount_spinbox.grid(row=1, column=4)
#discount_spinbox.bind('<Button-1>', confirmDiscount)

#Voucher
voucher_label = tk.Label(item_frame, text="Voucher code")
voucher_label.grid(row=0, column=5)
voucher_entry = tk.Entry(item_frame, width=20)
voucher_entry.grid(row=1, column=5)

#Remove item button
remove_sltd_item_btn = tk.Button(item_frame, text="Clear selection", command=clearSelectedItem)
remove_sltd_item_btn.grid(row=2, column=0, sticky="news", padx=20, pady=10)

#Add item button
add_item_btn = tk.Button(item_frame, text="Add to list", command=addItem)
add_item_btn.grid(row=2, column=1, columnspan=3, sticky="news", padx=20, pady=10)

#Fixed discount button
discount_var = tk.StringVar(value="NO")
applyDiscount_checkBtn = tk.Checkbutton(item_frame, text="Apply discount", variable=discount_var, onvalue="YES", offvalue="NO")
applyDiscount_checkBtn.grid(row=2, column=4, sticky="w")

#Apply voucher code
voucherState_var = tk.StringVar(value="NO")
redeemVoucher_Btn = tk.Button(item_frame, text="Redeam voucher", command=redeemVoucher)
redeemVoucher_Btn.grid(row=2, column=5, sticky="news")

#Item frame widget padding setting
for wgt in item_frame.winfo_children():
    wgt.grid_configure(padx=5, pady=5)

# #Button frame
# bottom_group_frame = tk.LabelFrame(invoice_tab)
# bottom_group_frame.grid(row=1, column=0, columnspan=1, sticky="news", padx=5, pady=10)

#Items frame stock list
top_r_frame = tk.LabelFrame(invoice_tab, text="Existing customers")
top_r_frame.grid(row=0, column=1, sticky="news", padx=2, pady=4)

##Customer information tree view in invoice page
dispCust_trv_Yscroll = ttk.Scrollbar(top_r_frame, orient='vertical')
dispCust_trv_Xscroll = ttk.Scrollbar(top_r_frame, orient='horizontal')
dispCust_trv = ttk.Treeview(top_r_frame, height=7, xscrollcommand=dispCust_trv_Xscroll.set, yscrollcommand=dispCust_trv_Yscroll.set)
dispCust_trv['columns'] = (1, 2, 3)
dispCust_trv['show'] = "headings"
dispCust_trv.column(1, width=100, anchor="c")
dispCust_trv.column(2, width=100, anchor="c")
dispCust_trv.column(3, width=50, anchor="c")

dispCust_trv.heading(1, text="First name")
dispCust_trv.heading(2, text="Last name")
dispCust_trv.heading(3, text="ID")

dispCust_trv.grid(row=0, column=0, columnspan=2, sticky="news")
dispCust_trv.bind("<Double-1>", selectCustomer)
highlight_row(dispCust_trv)
removeHighlight_row(dispCust_trv)
dispCust_trv_Yscroll.grid(row=0, column=2, sticky="news")
dispCust_trv_Xscroll.grid(row=1, column=0, columnspan=1, sticky="news")

bt_frame = tk.Frame(top_r_frame)
bt_frame.grid(row=2, column=0)

##Search customer names entry
searchCust_entry = tk.Entry(bt_frame, width=25)
searchCust_entry.bind('<KeyRelease>', searchCustomer)
searchCust_entry.grid(row=0, column=0, padx=4, pady=20, sticky="news")

##Search Customer names label
searchCust_label = tk.Label(bt_frame, text="Search")
searchCust_label.grid(row=0, column=1, pady=20, sticky="news")

## Select customer for invoice
selCustomer_button = tk.Button(bt_frame, text="Select", width=15, command=lambda:selectCustomer(selCustomer_button))
selCustomer_button.grid(row=0, column=2, padx=20, pady=20)

##Save invoice btn
saveInvoice_button = tk.Button(bottom_group_frame, text="Save invoice", width=15, command=checkAndSave)
saveInvoice_button.grid(row=0, column=0, padx=10)

newInvoice_button = tk.Button(bottom_group_frame, text="Create new invoice", width=15, command=createNewInvoice)
newInvoice_button.grid(row=0, column=1, padx=10)

editInvoice_button = tk.Button(bottom_group_frame, text="Edit invoice", width=15)
editInvoice_button.grid(row=0, column=2, padx=10)

removeAllItems_button = tk.Button(bottom_group_frame, text="Remove item(s)", width=15, command=deleteInvoiceItems)
removeAllItems_button.grid(row=0, column=4, padx=10)

grand_total_var = tk.StringVar(value="0.0")
grand_total_label = tk.Label(bottom_group_frame, text="Total:", font=('Times', 20))
grand_total_label.grid(row=0, column=5, sticky="news", padx=10)
grand_total_entry = tk.Entry(bottom_group_frame, textvariable=grand_total_var, state="readonly", width=11, font=('Times', 20))
grand_total_entry.grid(row=0, column=6, sticky="news", padx=10)

#Button widget padding setting
for wgt in bottom_group_frame.winfo_children():
    wgt.grid_configure(padx=3, pady=4)

invoiceItems_trv_frame = tk.Frame(bottom_group_frame, width= 10, height=10)
invoiceItems_trv_frame.grid(row=1, column=0, columnspan=7, sticky="news", padx=5, pady=5)

# Add a vertical Scrollbar
vertical_scroll = ttk.Scrollbar(invoiceItems_trv_frame, orient='vertical')
invoiceItems_trv = ttk.Treeview(invoiceItems_trv_frame, height=6, yscrollcommand=vertical_scroll.set)
invoiceItems_trv["columns"] = ("id", "item", "price", "qty", "total")
invoiceItems_trv["show"]="headings"
invoiceItems_trv.column("id", width=100, anchor='c')
invoiceItems_trv.column("item", width=300, anchor="c")
invoiceItems_trv.column("price", width=100, anchor="c")
invoiceItems_trv.column("qty", width=100, anchor="c")
invoiceItems_trv.column("total", width=110, anchor="c")

invoiceItems_trv.heading("id", text="ID")
invoiceItems_trv.heading("item", text="Item")
invoiceItems_trv.heading("price", text="Price")
invoiceItems_trv.heading("qty", text="Qty")
invoiceItems_trv.heading("total", text="Total")
invoiceItems_trv.grid(row=0, column=0, pady=4)
highlight_row(invoiceItems_trv)
removeHighlight_row(invoiceItems_trv)

#Configure and attach the scrollbar to widget
vertical_scroll.configure(command=invoiceItems_trv.yview)
vertical_scroll.grid(row=0, column=1, sticky="news")

#Main frame children padding setting
for wgt in notebook.winfo_children():
    wgt.grid_configure(padx=5, pady=5)

######## manage stock section begins #######

#Stock info frame
stock_info_frame = tk.LabelFrame(stock_tab)
stock_info_frame.grid(row=0, column=0, sticky="news", padx=3, pady=15)

btn_frame = tk.LabelFrame(stock_info_frame, text="Select action to perform")
btn_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=20)

radio_var = StringVar()
radio_var.set("addNewItem")
action = radio_var.get()
#Add new item
addNewItem_radioBtn = tk.Radiobutton(btn_frame, text="Add new item", 
                                     variable=radio_var, value="addNewItem", command=onSelectRadio)
addNewItem_radioBtn.grid(row=0, column=0, sticky="w")

#Update qty button
updateQty_radioBtn = tk.Radiobutton(btn_frame, text="Update Qty", 
                                    variable=radio_var, value="updateQty", command=onSelectRadio)
updateQty_radioBtn.grid(row=0, column=1, sticky="w")

#Update price
updatePrice_radioBtn = tk.Radiobutton(btn_frame, text="Update price", 
                                      variable=radio_var, value="updatePrice", command=onSelectRadio)
updatePrice_radioBtn.grid(row=0, column=2, sticky="w")

#Delete from stock
deleteItem_radioBtn = tk.Radiobutton(btn_frame, text="Delete from stock", 
                                      variable=radio_var, value="deleteItem", command=onSelectRadio)
deleteItem_radioBtn.grid(row=1, column=0, sticky="w")

#btn frame widget padding setting
for wgt in btn_frame.winfo_children():
    wgt.grid_configure(padx=5, pady=5)

#Item id
itemId_var = StringVar()
itemId_label = tk.Label(stock_info_frame, text="Item ID:")
itemId_label.grid(row=1, column=0)
itemId_entry = tk.Entry(stock_info_frame, width=20, textvariable=itemId_var)
itemId_entry.grid(row=1, column=1, sticky="w", padx=2)

#Item name or description
itemName_var = StringVar()
itemName_label = tk.Label(stock_info_frame, text="Description:")
itemName_label.grid(row=2, column=0)
itemName_entry = tk.Entry(stock_info_frame, width=20, textvariable=itemName_var)
itemName_entry.grid(row=2, column=1, sticky="w", padx=2)

#item price
itemPrice_var = StringVar()
itemPrice_label = tk.Label(stock_info_frame, text="Price:")
itemPrice_label.grid(row=3, column=0)
itemPrice_entry = tk.Entry(stock_info_frame, width=20, textvariable=itemPrice_var)
itemPrice_entry.grid(row=3, column=1, sticky="w", padx=2)

#item quantity
itemQty_var = StringVar()
itemQty_label = tk.Label(stock_info_frame, text="Quantity:")
itemQty_label.grid(row=4, column=0)
itemQty_entry = tk.Entry(stock_info_frame, width=20, textvariable=itemQty_var)
itemQty_entry.grid(row=4, column=1, sticky="w", padx=2)

#Wiget spacing
for wgt in stock_info_frame.winfo_children():
    wgt.grid_configure(padx=1, pady=5)


#Add stock button
updateStock_Btn = tk.Button(stock_info_frame, name="updateBtn", text="Add new item", width=15, command=manageStock)
updateStock_Btn.grid(row=5, column=1, padx=5, pady=10, sticky="w")

#Clear stock entry button
clearStock_Btn = tk.Button(stock_info_frame, text="Clear entry", width=15, command=clearStockEntry)
clearStock_Btn.grid(row=6, column=1, padx=5, pady=10, sticky="w")

#Select item for update btn
select_s_frame = tk.Frame(stock_tab)
select_s_frame.grid(row=0, column=1, pady=200, sticky="news")
slctBtn = tk.Button(select_s_frame, text="<<Select item", command=lambda:selectItemForUpdate(slctBtn))
slctBtn.grid(row=0, column=0, sticky="news")

#Show stock Tree view frame
stock_trv_frame = tk.LabelFrame(stock_tab, text="Stock")
stock_trv_frame.grid(row=0, column=2, sticky="news", padx=10, pady=2)

# Add tree view 1 vertical Scrollbar
stock_trv_vscroll = ttk.Scrollbar(stock_trv_frame, orient='vertical')
stock_trv = ttk.Treeview(stock_trv_frame, height=20, yscrollcommand=stock_trv_vscroll.set)
stock_trv["columns"] = ("id", "desc", "price", "instock")
stock_trv["show"]="headings"
stock_trv.column("id", width=80, anchor="c")
stock_trv.column("desc", width=300, anchor="c")
stock_trv.column("price", width=80, anchor="c")
stock_trv.column("instock", width=120, anchor="c")

stock_trv.heading("id", text="ID")
stock_trv.heading("desc", text="Description")
stock_trv.heading("price", text="Unit price")
stock_trv.heading("instock", text="Qty in stock")
stock_trv.grid(row=1, column=0, columnspan=3, pady=4)
stock_trv.bind("<Double-1>", selectItemForUpdate)
highlight_row(stock_trv)
removeHighlight_row(stock_trv)

#Configure and attach the scrollbar to widget
stock_trv_vscroll.configure(command=stock_trv.yview)
stock_trv_vscroll.grid(row=1, column=6, sticky="news")

searchBar_frame = tk.Frame(stock_trv_frame)
searchBar_frame.grid(row=0, column=0, padx=2, pady=5)
search_stock_entry = tk.Entry(searchBar_frame, width=30)
search_stock_entry.grid(row=0, column=0, padx=2, pady=5, sticky="w")
search_stock_entry.bind('<KeyRelease>', searchStockItem)
search_stock_label = tk.Label(searchBar_frame, text="Search")
search_stock_label.grid(row=0, column=1, sticky="news", padx=2, pady=5)

####### end ######

################# manage customer section begins #############
#Customer info frame
custInfo_frame = tk.LabelFrame(customer_tab)
custInfo_frame.grid(row=0, column=0, sticky="news", padx=10, pady=10)
#notebook.add(custInfo_frame, text="Customer info")

#First name
cFname_var = StringVar()
cFname_label = tk.Label(custInfo_frame, text="First name")
cFname_label.grid(row=0, column=0)
cFname_entry = tk.Entry(custInfo_frame, textvariable=cFname_var)
cFname_entry.grid(row=1, column=0, padx=5, pady=3, sticky="news")

#Last name
cLname_var = StringVar()
cLname_label = tk.Label(custInfo_frame, text="Last name")
cLname_label.grid(row=0, column=1)
cLname_entry = tk.Entry(custInfo_frame, textvariable=cLname_var)
cLname_entry.grid(row=1, column=1, padx=5, pady=3, sticky="news" )

#Customer name title
cTitle_var = StringVar()
cTitle_label = tk.Label(custInfo_frame, text="Title")
cTitle_label.grid(row=2, column=0)
cTitle_combobox = ttk.Combobox(custInfo_frame, textvariable=cTitle_var, values=["", "Mr.", "Mrs.", "Ms", "Miss", "Prof.", "Dr."])
cTitle_combobox.grid(row=3, column=0, padx=5, pady=3, sticky="news")

#Phone number
cPhone_var = StringVar()
cPhone_label = tk.Label(custInfo_frame, text="Phone number")
cPhone_label.grid(row=2, column=1)
cPhone_entry = tk.Entry(custInfo_frame, textvariable=cPhone_var)
cPhone_entry.grid(row=3, column=1, padx=5, pady=3, sticky="news")

#Address
cAddress_var = StringVar()
cAddress_label = tk.Label(custInfo_frame, text="Address")
cAddress_label.grid(row=4, column=0)
cAddress_entry = tk.Entry(custInfo_frame, textvariable=cAddress_var)
cAddress_entry.grid(row=5, column=0, columnspan=2, sticky="news", padx=5, pady=3)

#Add customer button
addCcustomer_button = tk.Button(custInfo_frame, text="Add customer", command=addCustomer)
addCcustomer_button.grid(row=8, column=0, padx=5, pady=20, sticky="news")

#update customer button
updtCustomer_button = tk.Button(custInfo_frame, text="Update customer info", command=updateCustomerInfo)
updtCustomer_button.grid(row=8, column=1, padx=5, pady=20, sticky="news")

#Clear entry button
clear_button = tk.Button(custInfo_frame, text="Clear entry", command=clearCEntry)
clear_button.grid(row=9, column=1, padx=5, pady=5, sticky="news")

#customer display frame
custDisplay_frame = tk.LabelFrame(customer_tab)
custDisplay_frame.grid(row=0, column=2, padx=10, pady=10, sticky="news")

#Select btn in manage customer tab
select_frame = tk.Frame(customer_tab)
select_frame.grid(row=0, column=1, pady=150, sticky="news")
sltBtn = tk.Button(select_frame, text="<<Select", command=lambda:selectCustomer(sltBtn))
sltBtn.grid(row=0, column=0, sticky="news")

#Search
search_frame = tk.Frame(custDisplay_frame)
search_frame.grid(row=0, column=0, sticky="news")

search_customer_entry = tk.Entry(search_frame, width=30)
search_customer_entry.grid(row=0, column=0, sticky="news", padx=10, pady=10)
search_customer_entry.bind('<KeyRelease>', searchCustomer)
search_customer_label = tk.Label(search_frame, text="Search")
search_customer_label.grid(row=0, column=2, sticky="w", padx=2, pady=10)

#Customer information tree view
custInfo_trv_vscroll = ttk.Scrollbar(custDisplay_frame, orient='vertical')
custInfo_trv = ttk.Treeview(custDisplay_frame, height=10, yscrollcommand=stock_trv_vscroll.set)
custInfo_trv['columns'] = (1, 2, 3, 4, 5, 6)
custInfo_trv['show'] = "headings"
custInfo_trv.column(1, width=70, anchor="c")
custInfo_trv.column(2, width=140, anchor="c")
custInfo_trv.column(3, width=140, anchor="c")
custInfo_trv.column(4, width=90, anchor="c")
custInfo_trv.column(5, width=150, anchor="c")
custInfo_trv.column(6, width=70, anchor="c")

custInfo_trv.heading(1, text="ID")
custInfo_trv.heading(2, text="First name")
custInfo_trv.heading(3, text="Last name")
custInfo_trv.heading(4, text="Phone")
custInfo_trv.heading(5, text="Address")
custInfo_trv.heading(6, text="Title")

custInfo_trv.grid(row=1, column=0, columnspan=2, sticky="news")
custInfo_trv_vscroll.grid(row=1, column=2, sticky="nws")
custInfo_trv.bind("<Double-Button-1>", selectCustomer)
highlight_row(custInfo_trv)
removeHighlight_row(custInfo_trv)

#Delete customer(s)
delCustomer_button = tk.Button(custDisplay_frame, width=15, text="Delete customer", command=deleteCustomer)
delCustomer_button.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

################ end ############################

################ Sales section begins #####################
sales_left_frame = tk.LabelFrame(sales_tab)
sales_left_frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)
radio_btn_frame = tk.Frame(sales_left_frame)
radio_btn_frame.grid(row=0, column=0, columnspan=4, sticky="nws")
sradio_var = StringVar()
sradio_var.set("allItems")

# all item sales
allItems_radioBtn = tk.Radiobutton(radio_btn_frame, text="All items", 
                                     variable=sradio_var, value="allItems", command=onSelectSalesRadio)
allItems_radioBtn.grid(row=0, column=0, sticky="w")

#specific item sales
specificItem_radioBtn = tk.Radiobutton(radio_btn_frame, text="Specific item", 
                                    variable=sradio_var, value="specificItem", command=onSelectSalesRadio)
specificItem_radioBtn.grid(row=0, column=1, sticky="w")

##Start date for sales records
searCombo_label = tk.Label(sales_left_frame, text="ID:")
searCombo_label.grid(row=1, column=0, sticky="news")

## filter by id combo
c = tk.StringVar()
itemIdCombo = ttk.Combobox(sales_left_frame, textvariable=c)
itemIdCombo.grid(row=1, column=1, sticky="news")
itemIdCombo.configure(state="readonly")
itemIdCombo.bind("<<ComboboxSelected>>", searchNameById)
#itemIdCombo.bind('<KeyRelease>', searchSales)

##
searCombo_label = tk.Label(sales_left_frame, text="Name:")
searCombo_label.grid(row=1, column=2, sticky="news")

## filter by name combo
n = tk.StringVar()
itemNameCombo = ttk.Combobox(sales_left_frame, textvariable=n)
itemNameCombo.grid(row=1, column=3, sticky="news")
itemNameCombo.configure(state="readonly")
itemNameCombo.bind("<<ComboboxSelected>>", searchIdByName)
#itemNameCombo['values'] = (fillItemNameCombo())

fromLabel = tk.Label(sales_left_frame, text="From:")
fromLabel.grid(row=3, column=0, sticky="news")

fromEntry = tk.Entry(sales_left_frame)
fromEntry.grid(row=3, column=1, sticky="news")

toLabel = tk.Label(sales_left_frame, text="To:")
toLabel.grid(row=3, column=2, sticky="news")

toEntry = tk.Entry(sales_left_frame)
toEntry.grid(row=3, column=3, sticky="news")

##
filter_sales_btn = tk.Button(sales_left_frame, text="Filter sales", command=filterSales)
filter_sales_btn.grid(row=4, column=1, sticky="news")

##
export_sales_btn = tk.Button(sales_left_frame, text="Export", command=exportSalesRecords)
export_sales_btn.grid(row=4, column=3, sticky="news")

#Wiget spacing
for wgt in sales_left_frame.winfo_children():
    wgt.grid_configure(padx=2, pady=5)

fDateFormat_lable = tk.Label(sales_left_frame, text="yyyy-mm-dd")
fDateFormat_lable.grid(row=2, column=1, sticky="ews")

tDateFormat_lable = tk.Label(sales_left_frame, text="yyyy-mm-dd")
tDateFormat_lable.grid(row=2, column=3, sticky="ews")

searchSales_label = tk.Label(sales_left_frame, text="Search")
searchSales_label.grid(row=5, column=2, pady=15, sticky="w")
searchSales_entry = tk.Entry(sales_left_frame)
searchSales_entry.grid(row=5, column=1, pady=15, sticky="news")
searchSales_entry.bind('<KeyRelease>', searchList)

search_Yscroll = ttk.Scrollbar(sales_left_frame, orient='vertical')
search_trv = ttk.Treeview(sales_left_frame, height=4, yscrollcommand=search_Yscroll.set)
search_trv["columns"] = (1, 2)
search_trv["show"]="headings"
search_trv.column(1, width=70, anchor=CENTER)
search_trv.column(2, width=110, anchor=CENTER)

search_trv.heading(1, text="ID")
search_trv.heading(2, text="Item")
search_trv.grid(row=6, column=0, columnspan=4, pady=3, sticky="news")
search_Yscroll.grid(row=6, column=5, pady=3, sticky="nws")
search_Yscroll.configure(command=search_trv.yview)
search_trv.bind('<Double-1>', selectItemInSearchSales)
highlight_row(search_trv)
removeHighlight_row(search_trv)

# Add a vertical Scrollbar
sales_Yscroll = ttk.Scrollbar(sales_tab, orient='vertical')
sales_trv = ttk.Treeview(sales_tab, height=15, yscrollcommand=sales_Yscroll.set)
sales_trv["columns"] = (1, 2, 3, 4, 5, 6)
sales_trv["show"]="headings"
sales_trv.column(1, width=80, anchor='c')
sales_trv.column(2, width=160, anchor="c")
sales_trv.column(3, width=100, anchor="c")
sales_trv.column(4, width=100, anchor="c")
sales_trv.column(5, width=100, anchor="c")
sales_trv.column(6, width=100, anchor="c")

sales_trv.heading(1, text="ID")
sales_trv.heading(2, text="Item")
sales_trv.heading(3, text="Unit price")
sales_trv.heading(4, text="Qty")
sales_trv.heading(5, text="Total")
sales_trv.heading(6, text="Date")
sales_trv.grid(row=0, column=1, pady=4)
highlight_row(sales_trv)
removeHighlight_row(sales_trv)

#Configure and attach the scrollbar to widget
sales_Yscroll.configure(command=sales_trv.yview)
sales_Yscroll.grid(row=0, column=2, sticky="news")

resultBar = tk.Frame(sales_tab)
resultBar.grid(row=1, column=1)

totalQty_var = StringVar()
totalQty_label = tk.Label(resultBar, text="Total qty:", font=('Times', 15))
totalQty_label.grid(row=0, column=0, pady=15, sticky="w")
totalQty_entry = tk.Entry(resultBar, state="readonly", textvariable=totalQty_var, width=15, font=('Times', 15))
totalQty_entry.grid(row=0, column=1, padx=5, pady=15, sticky="news")
 
totalSales_var = StringVar()
totalSales_label = tk.Label(resultBar, text="Total sales:", font=('Times', 15))
totalSales_label.grid(row=0, column=2, padx=5, pady=15, sticky="w")
totalSales_entry = tk.Entry(resultBar, state="readonly", textvariable=totalSales_var, width=15, font=('Times', 15))
totalSales_entry.grid(row=0, column=3, padx=5, pady=15, sticky="news")

################ Sales section ends #####################

#Show all items
showAllItems(stockList_trv)
showAllItems(stock_trv)

#Display customer list
showCustomers()

#Show items in sales
showItemsInSales()
showAllSales()

#Main app window loop
window.mainloop()