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
    A link to a file in the site. See below

Adding new type of column is not hard, but remember to stay simple: we don't want to rewrite `PloneFormGen`__ from scratch!
Also: there's **no validation**!

__ http://plone.org/products/ploneformgen

You can add as many columns as you want; users that will fill your table won't be able to change what you have defined.

Filling the table
-----------------

Configuration is not changing anything on your layour, but users with *Contributor* role on this document will see a
new tab: "**Edit table**".

.. image:: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-01.png/image_large
   :alt: Page with Table view 
   :target: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-01.png

When accessing the "*Edit table data*" view users will be able to add new rows to the table and edit their own rows.
The data form given to the user is generated using the configuration options that the document creator defined before.

.. image:: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-03.png/image_large
   :alt: Add new row in the table 
   :target: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-03.png

Some note:

* Every added row is put at the end of the table
* Every Contributor is able to edit or delete his own rows
* Users with "*Editor*" roles is able to edit or delete all rows
* Users with "*Editor*" roles is able change row order

.. image:: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-04.png/image_large
   :alt: Table editing
   :target: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-04.png

When switching back to main document view, the generated table is part of the document body text.

.. image:: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-05.png/image_large
   :alt: Page with Table view
   :target: http://blog.redturtle.it/pypi-images/collective.tablepage/collective.tablepage-0.1-05.png

Download and Upload data
------------------------

* You can optionally display a link for download the table content as a CSV
  (activate the "*Show download link for data*" from "*Settings*")
* Contributors can populate the table uploading a CSV file

Column of type "File"
---------------------

Column of type "File" are the most complex.

When adding or editing a row the user is able to upload a new file, creating a new Plone File content, or selecting
an existing file from the site.

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


