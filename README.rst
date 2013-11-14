A new Plone content type similar to the standard Page but with a **table as main content**.

.. contents:: **Table of contents**

Introduction
============

This product want to give to site members a simple way to manage a page with a table inside in a collaborative way.
To be more precise, it's focused on contents where the table is the main scope of the page.

The only other option is to create the page using the WYSIWYG editor (like TinyMCE), then leave
to editors power to modify it, but:

* using TinyMCE commands for table is not so easy (users sometimes mess up your pre-defined layout)
* you can't prohibit users to delete or change rows added from other users, or adding new column you don't want.

If you need to beat those limits but you still simply need a Plone page, this is product is probably what you need.

If you need to store a *huge* amount of data, you should probably look for other solutions.

How to use
==========

After installation you will see a new addable content type: the **Page with Table**.

Some fields of this new content types are very similar to Page ones, although the "**Body Text**" field is splitted
in two separated sections (text before and after the table).

Configuring the table
---------------------

The most important field is "**Columns**", where you can define the column structure of you table.

.. image:: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-02.png/image_large
   :alt: Page with Table configuration 
   :target: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-02.png

For every column you can define some information like header's content and other description, but you must also define
the *type* of data in the column.

Right now you can choose from:

``String``
    A simple line of text, the most common type.
``Text``
    A textarea, for saving more text and take care of carriage returns.
``Select``
    Still a simple line of thext, but user must choose it from a vocabulary you will define (in the proper column
    of the configuration).
``File``
    A link to a file in the site. See below.
``Files``
    Same as ``File`` above, but for multiple files.
``Link``
    A link to an URL, or an internal site document. It use Plone reference browser native widget.

Adding new type of column is not hard, but remember to stay simple: we don't want to rewrite `PloneFormGen`__ from scratch!
Also: there's **no validation**!

__ http://plone.org/products/ploneformgen

You can add as many columns as you want; users that will fill your table won't be able to change what you have defined.

Filling the table
-----------------

Configuration is not changing anything in your layour, but users with *Contributor* role on this document will see a
new tab: "**Edit table**".

.. image:: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-01.png/image_large
   :alt: Page with Table view 
   :target: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-01.png

When accessing the "*Edit table data*" view, users will be able to add new rows to the table and edit their own rows.
The form given to the user is generated using the configuration options that the document creator defined before.

.. image:: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-03.png/image_large
   :alt: Add new row in the table 
   :target: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-03.png

Some note:

* Every added row is put at the end of the table or at the end of section (see below)
* Every Contributor is able to edit or delete his own rows
* Users with "*Editor*" roles are able to edit or delete all rows
* Users with "*Editor*" roles are able change row order

.. image:: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-04.png/image_large
   :alt: Table editing
   :target: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-04.png

When switching back to main document view the generated table is part of the document body text.

.. image:: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-05.png/image_large
   :alt: Page with Table view
   :target: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-05.png

Table labels and sections
-------------------------

.. image:: https://raw.github.com/RedTurtle/collective.tablepage/b4d92e346ce9ae6cbd9de053eeee158088b85b67/collective/tablepage/browser/images/labeling.png
   :alt: New label icon
   :align: left

Users with power of configuring the table can also add a special type or row: **Label**. Apart the UI changes,
labels break the table in groups of logical rows: every group start at the position of the label at end at
the next label (or at the end of the table).

If one or more labels are used, contributors will be able to add new rows at the end of the section instead
of adding only at the end of the table.

Download and Upload data
------------------------

.. image:: https://raw.github.com/RedTurtle/collective.tablepage/36961df4ddfd49daa014375e8956db878780e726/collective/tablepage/browser/images/download_data.png
   :alt: Download CSV icon
   :align: left

Data stored  in the table can be downloaded, and optionally you can display a download link also to page visitors
(activate the "*Show download link for data*" inside "*Settings*").
When the download icon is used in the "*Edit table*" view, downloaded data is compatible to the upload CSV feature
described above (columns ids are used instead of titles, contents uids instead of URL to referenced contents, ...) 

.. image:: https://raw.github.com/RedTurtle/collective.tablepage/36961df4ddfd49daa014375e8956db878780e726/collective/tablepage/browser/images/upload_data.png
   :alt: Upload CSV icon
   :align: left

Contributors can also upload data using a CSV file. The file *must* provide a row with column ids defined in the
configuration. Columns with unknow id are ignored.

Column of type "File" and "Files"
---------------------------------

Columns of type file(s) are the most complex.

When adding or editing a row the user is able to upload new files, creating a new Plone File content, or selecting
existing files from the site.

In both cases permissions matters: the user must have permisson of adding new file in the storage folder or see it.
The storage folder is configured by the document creator.

When rendering the table, a link to download the file is displayed.
 
Other products
==============

There are at least two other products for Plone that are focused on table generation:

`collective.table`__
    This product is focused on the editing part (and the use of DataTables jQuery plugin is nice), but
    it dowsn't work on Plone 3 and you have no way of limit the power of users on the table.
`collective.pfg.soup`__
    Very powerful, modular and extensible. It's using PloneFormGen as table configuration and can store *a lot* of data.
    Unluckily it has a lot of dependencies and it won't run on Plone 3.

__ https://pypi.python.org/pypi/collective.table/
__ https://pypi.python.org/pypi/collective.pfg.soup/

Requirements
============

This product can be used with al version of Plone from 3.3 to 4.3.

For Plone 3.3 you need some special configuration like:

* A `custom branch of DataGridField`__ where we backported some new features from 1.8 branch
* Available table styles are taken from TinyMCE configuration, so you must use it instead of Kupu
* No versioning support is available

__ https://github.com/RedTurtle/Products.DataGridField/tree/1.6

Credits
=======

Developed with the support of:

* `Azienda USL Ferrara`__

  .. image:: http://www.ausl.fe.it/logo_ausl.gif
     :alt: Azienda USL's logo
  
* `S. Anna Hospital, Ferrara`__

  .. image:: http://www.ospfe.it/ospfe-logo.jpg 
     :alt: S. Anna Hospital logo

All of them supports the `PloneGov initiative`__.

__ http://www.ausl.fe.it/
__ http://www.ospfe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.
  
.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/


