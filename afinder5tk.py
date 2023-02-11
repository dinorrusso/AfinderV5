#!/usr/bin/env python3
# from re import T, X
# import tkinter as tk
# from tkinter import BOTTOM, LEFT, SUNKEN, TOP, Label, ttk
#from asyncio.log import logger
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from tkinter import *
from tkinter.ttk import Separator, Style, Treeview
from unittest import result
from PIL import Image, ImageTk
from dotenv import load_dotenv
import os
import aflog
import sqlite_ops as sq_ops
import jamf_req
import jira_req
import pyperclip as pc
from jira import JIRA
from pathlib import Path
import sys


#TODO
# maybe add scrollbar(s) to treeview

class AFinder(Tk):
    TITLE='AFinder v5'
    logger = aflog.logging.getLogger(__name__)
    
    if getattr(sys, 'frozen', False):
        #running in a bundle
        bundle_dir = sys._MEIPASS
    else:
        #running in python env
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
   
    logger.info('bundle_dir={}'.format(bundle_dir))

    load_dotenv(bundle_dir + '/.env')

    database_flename = 'computers.db'
    connection = NONE
    clipboard_text = ''
    database_folder = bundle_dir + '/data/'
    refresh_folder = Path(os.path.expanduser('~/Downloads/'))
    image_folder = bundle_dir+'/images/'

    def __init__(self):
        super().__init__()
        self.InitUI()

    def InitUI(self):
        self.title(self.TITLE)
        self.resizable(True, True)

        window_width = 800
        window_height = 650

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # find the center point
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        #image
        image_frame = Frame(self, )
        image_frame.pack(side=TOP, fill=X, padx = 5 , pady = 5)
        # Create an object of tkinter ImageTk
        
        image_file = self.image_folder + 'afinder_icon.png' 
        #If you want to add on to the path, you can use the / operator directly in your code. 
        # Say goodbye to typing out os.path.join(a, b) over and over.
        self.logger.info(image_file)
        self.img = Image.open(image_file)
        self.icon=self.img.resize((50,50))
        self.render=ImageTk.PhotoImage(self.icon)
        self.image_label=Label(image_frame, image=self.render)
        self.image_label.pack(side=RIGHT)


        # database widgets
        db_button_frame = Frame(self)
        db_button_frame.pack(side=TOP, fill=X, padx = 5 , pady = 10)

        # connect to DB button
        # self.connect_button = Button(
        #     db_button_frame,
        #     text='Connect to DB',
        #     width=10,
        #     command=self.on_connect
        # )
        # self.connect_button.pack(side=LEFT)
        #db label
        self.db_label = Label(db_button_frame, text='No database connected', anchor='w')
        self.db_label.pack(side=LEFT)

        refresh_frame = Frame(self)
        refresh_frame.pack(side=TOP, fill=X, padx = 5 , pady = 0)

        # refresh DB button
        self.refresh_button = Button(
            refresh_frame,
            text='Refresh DB',
            width=10,
            command=self.on_refresh 
        )
        self.refresh_button.pack(side=LEFT)

        #refresh label
        self.refresh_label = Label(refresh_frame, text='', anchor='w')
        self.refresh_label.pack(side=LEFT)
        #separator
        separator_frame = Frame(self)
        separator_frame.pack(side=TOP, fill=X, padx = 5 , pady = 5)
        separator = Separator(separator_frame, orient='horizontal')
        separator.pack(fill='x')

        #email entry area
        email_frame = Frame(self)
        email_frame.pack(side=TOP, fill=X, padx = 5 , pady = 10)
        self.email_label = Label(email_frame, text='User Email:', anchor='w')
        self.email_label.pack(side=LEFT)
        self.email_address = ''
        self.email_entry = Entry(email_frame,textvariable=self.email_address)
        self.email_entry.pack(side=LEFT, fill=X, expand=True)
        self.email_entry.bind('<Return>', self.on_return)
        lyftdotcom_label = Label(email_frame, text='@lyft.com is optional')
        lyftdotcom_label.pack(side=RIGHT)



        #asset data found 
        found_label_frame = Frame(self)
        found_label_frame.pack(side=TOP, fill=X, padx = 5 , pady = 5)
        found_label=Label(found_label_frame, text='Assets Data Found')
        found_label.pack(side=LEFT)

        # search button fits nicely here
        self.search_button = Button(
            found_label_frame,
            text='Search',
            width=10,
            command=self.on_search
        )
        self.search_button.pack(side=RIGHT)


        #asset data 
        tree_frame = Frame(self)
        tree_frame.pack(side=TOP, fill=X, padx = 5 , pady = 0)
        self.asset_tree = Treeview(tree_frame, show='headings', height=12)
        self.asset_tree['columns'] =('source', 'asset')
        self.asset_tree.column('#0', width=0, stretch=NO)
        self.asset_tree.column('source', width=150, anchor=W, stretch=NO)
        self.asset_tree.column('asset', width=400,anchor=W)

        self.asset_tree.heading('#0', text='', anchor=W)
        self.asset_tree.heading('source', text='Source', anchor=W)
        self.asset_tree.heading('asset', text='Asset Information', anchor=W)
        self.asset_tree.pack(side=TOP, fill=X, padx = 5 , pady = 0)

        #check boxes
        cb_frame = Frame(self)   
        cb_frame.pack(side=TOP, fill=X, padx = 5 , pady = 5)
        self.cmdb = BooleanVar()
        self.jamf = BooleanVar()
        self.jira = BooleanVar()
        self.cmdb_cb = Checkbutton(cb_frame, text='CMDB', variable = self.cmdb, onvalue = True, offvalue = False)
        self.cmdb_cb.pack(side=LEFT)
        self.jamf_cb = Checkbutton(cb_frame, text='JAMF', variable = self.jamf, onvalue = True, offvalue = False)
        self.jamf_cb.pack(side=LEFT)
        self.jira_cb = Checkbutton(cb_frame, text='Jira OB Tickets', variable = self.jira, onvalue = True, offvalue = False)
        self.jira_cb.pack(side=LEFT)
        self.cmdb_cb.select()
        self.jamf_cb.select()
        self.jira_cb.select()

        #operations
        ops_button_frame = Frame(self)
        ops_button_frame.pack(side=TOP, fill=X, padx = 5 , pady = 10)

        # copy all button
        self.copy_all_button = Button(
            ops_button_frame,
            text='Copy All',
            width=10,
            command=self.on_copy_all
        )
        self.copy_all_button.pack(side=LEFT)

        # copy selected button
        self.copy_selected_button = Button(
            ops_button_frame,
            text='Copy Selected',
            width=10,
            command=self.on_copy_selected
        )
        self.copy_selected_button.pack(side=LEFT)
        # clear button
        self.clear_button = Button(
            ops_button_frame,
            text='Clear',
            width=10,
            command=self.on_clear 
        )
        self.clear_button.pack(side=LEFT)

        #offboard ticket widgets
        ofb_frame = Frame(self)   
        ofb_frame.pack(side=TOP, fill=X, padx = 5 , pady = 5)
        ofb_label = Label(ofb_frame, text='Jira OFB Ticket ID: ', anchor='w')
        ofb_label.pack(side=LEFT)
        self.ofb_ticket = ''
        self.ofb_entry = Entry(ofb_frame,textvariable=self.ofb_ticket)
        self.ofb_entry.pack(side=LEFT, fill=X, expand=True)
        self.add_comment_button = Button(
            ofb_frame,
            text='Add Comment',
            width=10,
            command=self.on_add_comment
        )
        self.add_comment_button.pack(side=RIGHT)


        #status bar
        self.status_bar_status = ' Database not connected. Press <Connect to DB> to start.'
        self.statusbar = Label(self, text=self.status_bar_status, bd=1, relief=SUNKEN, anchor=W)
        self.statusbar.pack(side=BOTTOM, fill=X)
#----------------------------------------------------------------
        #go ahead and connect to db automatically
        self.connection = sq_ops.create_connection(self.database_folder + self.database_flename)
        #database_filename = filename
        self.statusbar['text'] = ' Database connected - enter email to search.'
        self.db_label['text'] = 'DB: {}'.format(self.database_folder + self.database_flename)
        self.refresh_label['text'] = 'Last refresh: {}'.format(sq_ops.get_refresh_time(self.connection))
        self.enable_widgets()


    def init_widget_states(self):
        # most widgets are diabled until database is connected
        self.connect_button['state']=NORMAL
        self.connect_button.focus_set()
        self.refresh_button['state']=DISABLED
        self.search_button['state']=DISABLED
        self.copy_all_button['state']=DISABLED
        self.copy_selected_button['state']=DISABLED
        self.clear_button['state']=DISABLED
        self.add_comment_button['state']=DISABLED
        #check boxes
        self.cmdb_cb['state']=DISABLED
        self.jamf_cb['state']=DISABLED
        self.jira_cb['state']=DISABLED
        # entry widgets
        self.email_entry['state']=DISABLED
        self.ofb_entry['state']=DISABLED

    def enable_widgets(self):
        # enable widgets when database is connected
        self.refresh_button['state']=NORMAL
        self.search_button['state']=NORMAL
        self.copy_all_button['state']=NORMAL
        self.copy_selected_button['state']=NORMAL
        self.clear_button['state']=NORMAL
        self.add_comment_button['state']=NORMAL
        #check boxes
        self.cmdb_cb['state']=NORMAL
        self.jamf_cb['state']=NORMAL
        self.jira_cb['state']=NORMAL
        # entry widgets
        self.email_entry['state']=NORMAL
        self.email_entry.focus_set()
        self.ofb_entry['state']=NORMAL

    def on_connect(self):
        self.logger.info('on_connect')
        filename = ''
        filetypes = (
            ('database files', '*.db'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename(
            title='Open database',
            initialdir=self.database_folder,
            filetypes=filetypes)

        self.logger.info('Selected db file: {}'.format(filename))
        
        #dialog box 
        # showinfo(
        #     title='Selected Files',
        #     message=filename
        # )

        if filename != '':
            self.connection = sq_ops.create_connection(filename)
            database_filename = filename
            self.statusbar['text'] = ' Database connected - enter email to search.'
            self.db_label['text'] = 'DB: {}'.format(database_filename)
            self.refresh_label['text'] = 'Last refresh: {}'.format(sq_ops.get_refresh_time(self.connection))
            self.enable_widgets()

    def on_refresh(self):
        self.logger.info('on_refresh')
        filename = ''
        filetypes = (
            ('csv files', '*.csv'),
            ('All files', '*.*')
        )
        self.logger.info('refresh_folder={}'.format(self.refresh_folder))
        filename = fd.askopenfilename(
            title='Open csv file',
            initialdir=self.refresh_folder,
            filetypes=filetypes)

        self.logger.info('Selected csv file: {}'.format(filename))
        
        #dialog box 
        # showinfo(
        #     title='Selected Files',
        #     message=filename
        # )

        if filename != '':
            sq_ops.create_cherwell_table(self.connection, filename)
            self.statusbar['text'] = ' Database refresh complete using ' + filename +'.'
            self.refresh_label['text'] = 'Last refresh: {}'.format(sq_ops.get_refresh_time(self.connection))
        
    def on_search(self):
        #get the search token from the entry widget
        search_token = self.email_entry.get()

        #before displaying clear asset tree
        for item in self.asset_tree.get_children():
            self.asset_tree.delete(item)

        #add @lyft.com to search token if necessary
        if search_token[-9:] != '@lyft.com':
            search_token += '@lyft.com'
        self.logger.info('search token = {}'.format(search_token))
        self.logger.info('cmdb={} jamf={}, jira = {}'.format(self.cmdb, self.jamf, self.jira))
        # set a results counter
        results_counter = 0
        #if cmdb selected search database and display results
        if self.cmdb.get():
            results = sq_ops.select_all_cw_by_email(self.connection, search_token)
            results_counter += len(results)
            if len(results) == 0:
                self.asset_tree.insert('', END, values=('CMDB', '[No matches found]'))
            else:
                for result in results:
                    self.asset_tree.insert('', END, values=('CMDB', '['+result[0] +'] ['+ result[1] + '] ['+ result[2] + ']'))
        #if jamf selected query via api and display results
        if self.jamf.get():
            results = jamf_req.get_jamf_devices(search_token)
            results_counter += len(results)
            if len(results) == 0:
                self.asset_tree.insert('', END, values=('JAMF', '[No matches found]'))
            else:
                for result in results:
                    self.asset_tree.insert('', END, values=('JAMF', result))
        #if jira selected query via api and display results
        if self.jira.get():
            results = jira_req.get_jira_devices(search_token)
            results_counter += len(results)
            if len(results) == 0:
                self.asset_tree.insert('', END, values=('JIRA', '[No matches found]'))
            else:
                for result in results:
                    self.asset_tree.insert('', END, values=('JIRA', result))
        #update the status bar with results info
        self.statusbar['text'] = ' ' + str(results_counter) + ' results found.'

    def on_return(self, e):
        self.logger.info('e: {}'.format(e))
        self.on_search()

    def on_clear(self):
        self.logger.info('on_clear')
        #clear data from widgets and clipboard
        self.statusbar['text'] = ''
        self.email_entry.delete(0,END)
        self.ofb_entry.delete(0,END)
        for item in self.asset_tree.get_children():
            self.asset_tree.delete(item)
        self.clipboard_text = ''
        self.email_entry.focus_set()

    def on_copy_all(self):
        #clear the clipboard text
        self.clipboard_text = ''
        results_counter = 0
        #get all values from treeview 
        for child in self.asset_tree.get_children():
            #self.logger.info('item = {}'.format(child))
            #self.logger.info(self.asset_tree.item(child,'values'))
            entry = self.asset_tree.item(child,'values')
            result_str = ''
            #unpack the tuple
            for values in entry:
                result_str += values + ' '
            self.clipboard_text += result_str.rstrip() + '\n'
            results_counter += 1
        #copy results text to clipboard
        pc.copy(self.clipboard_text)
        self.statusbar['text'] = ' ' + str(results_counter) + ' item(s) copied to clipboard.'


    def on_copy_selected(self):
        #clear the clipboard text
        self.clipboard_text = ''
        results_counter = 0
        #get selected rows indexes
        selections = self.asset_tree.selection()
        
        for sel in selections:
            results_counter += 1
            #unpack the list
            result_str = ''
            for values in self.asset_tree.item(sel)['values']:
                result_str += values + ' '
            self.clipboard_text += result_str + '\n'
        #copy results text to clipboard
        pc.copy(self.clipboard_text)
        self.statusbar['text'] = ' ' + str(results_counter) + ' item(s) copied to clipboard.'

    def on_add_comment(self):
       
        user = os.environ.get("JIRAUSERNAME")
        pw = os.environ.get("JIRAPASSWORD")
        server= os.environ.get("JIRASERVER")
        

        try:
            #authenticate
            jira = JIRA(server=server, basic_auth=(user, pw))
            # Get the issue id from user
            issue = jira.issue(self.ofb_entry.get())
            #copy the text for the comment from the clipboard
            comment_text = self.clipboard_text
            # Add the comment to the issue.
            jira.add_comment(issue, comment_text)
            self.statusbar['text']=' Comment added to: ' + self.ofb_entry.get()
        except Exception as e:
            self.statusbar['text']=' Add unsuccessful: ' + str(e)


if __name__ == "__main__":
    app = AFinder()
    app.mainloop()


