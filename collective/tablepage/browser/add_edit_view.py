from plone.dexterity.browser.add import DefaultAddForm as BaseAddForm            
from plone.dexterity.browser.add import DefaultAddView as BaseAddView            
from plone.dexterity.browser.edit import DefaultEditForm as BaseEdit             
from plone.dexterity.interfaces import IDexterityEditForm                        
from plone.z3cform import layout
from zope.interface import classImplements
from z3c.form import button
from plone.dexterity.i18n import MessageFactory as _dmf                           
from collective.tablepage import tablepageMessageFactory as _
from zope.interface import Invalid                                               
from z3c.form.interfaces import WidgetActionExecutionError
from collective.tablepage import config
from Products.statusmessages.interfaces import IStatusMessage                             
from plone.dexterity.events import AddCancelledEvent
from plone.dexterity.events import AddCancelledEvent                             
from plone.dexterity.events import EditCancelledEvent                            
from plone.dexterity.events import EditFinishedEvent
from zope.event import notify
import re


def change_widget(widgets):
    widgets['pageColumns'].allow_reorder = True


def validate_pageColumns(data):
    ids = []
    for row in data.get('pageColumns'):
        id = row.get('id', '')
        try:
            ids.index(id)
            raise WidgetActionExecutionError(
                'pageColumns', 
                Invalid(_('pagecolumn_validation_error_duplicated_id',
                        default=u'Id "${col_name}" is duplicated',
                        mapping={'col_name': id})
                )
            )
        except ValueError:
            ids.append(id)
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9.\-_]*$", id):
            'pageColumns', 
            raise WidgetActionExecutionError(
                Invalid(_('pagecolumn_validation_error_id_format',
                        default=u'Invalid value: "${col_name}". "Column Id" must not contains special characters',
                        mapping={'col_name': id})
                )
            )
        if id in config.RESERVED_IDS:
            raise WidgetActionExecutionError(
                Invalid(_('pagecolumn_validation_error_id_invalid',
                        default=u'A reserved value has been used for "id"')
                )
            ) 


class DefaultEditForm(BaseEdit):                             
    """                                                                             
    """                                                                             
    def updateWidgets(self):                                                     
        super(DefaultEditForm, self).updateWidgets()                             
        change_widget(self.widgets)   

    @button.buttonAndHandler(_dmf(u'Save'), name='save')                             
    def handleApply(self, action):                                                  
        data, errors = self.extractData()                                                                                       
        if errors:                                                                  
            self.status = self.formErrorsMessage                                    
            return

        validate_pageColumns(data)

        self.applyChanges(data)                                                
        IStatusMessage(self.request).addStatusMessage(                              
            _dmf(u"Changes saved"), "info")                                          
        self.request.response.redirect(self.nextURL())                              
        notify(EditFinishedEvent(self.context))                                     
                                                                                    
    @button.buttonAndHandler(_dmf(u'Cancel'), name='cancel')                         
    def handleCancel(self, action):                                                 
        IStatusMessage(self.request).addStatusMessage(                              
            _dmf(u"Edit cancelled"), "info")                                         
        self.request.response.redirect(self.nextURL())                              
        notify(EditCancelledEvent(self.context)) 

                                                                                    
DefaultEditView = layout.wrap_form(DefaultEditForm)                                 
classImplements(DefaultEditView, IDexterityEditForm)


class DefaultAddForm(BaseAddForm):                        
    """                                                                          
    """                                                                          
    def updateWidgets(self):                                                     
        super(DefaultAddForm, self).updateWidgets()                              
        change_widget(self.widgets)   

    @button.buttonAndHandler(_dmf('Save'), name='save')                                
    def handleAdd(self, action):                                                    
        data, errors = self.extractData()                                           
        if errors:                                                                  
            self.status = self.formErrorsMessage                                    
            return   
        
        validate_pageColumns(data)

        obj = self.createAndAdd(data)                                               
        if obj is not None:                                                         
            # mark only as finished if we get the new object                        
            self._finishedAdd = True                                                
            IStatusMessage(self.request).addStatusMessage(                          
                self.success_message, "info"                                        
            )                                                                       
                                                                                    
    @button.buttonAndHandler(_dmf(u'Cancel'), name='cancel')                           
    def handleCancel(self, action):                                                 
        IStatusMessage(self.request).addStatusMessage(                              
            _dmf(u"Add New Item operation cancelled"), "info"                          
        )                                                                           
        self.request.response.redirect(self.nextURL())                              
        notify(AddCancelledEvent(self.context))                                     
        

    def nextURL(self):                                                           
        return self.context.absolute_url()                                                          
                                                                                 
                                                                                 
class DefaultAddView(BaseAddView):                                               
                                                                                 
    form = DefaultAddForm 
