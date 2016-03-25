from datetime import date
from openerp import fields,api,models
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

class TodoTask(models.Model):
	_name = 'todo.task'
	_inherit = ['todo.task', 'mail.thread']


	# def email_task(self):
	# 	mail = self.env['mail.mail']
	# 	mail_ids = []
	# 	email_to = "prasoon360@gmail.com"
	# 	subject = "Hai"
	# 	body = "How are you?"
	# 	footer = "Regards"
	# 	y = (mail.create({ 'email_to': email_to,
 #            'subject': subject,
 #            'body_html': '<pre><span class="inner-pre" style="font-size: 15px">%s<br>%s</span></pre>' %(body, footer)
 #         }))
	# 	self._context=None
	# 	mail_ids.append(y.id)
	# 	mail.send()
	# 	return True

	
	def email_task(self):
		message_obj = self.env['mail.message']
		mail_obj = self.env['mail.mail']
		email_template_obj = self.env['email.template']
		email_compose_message_obj = self.env['mail.compose.message']
		message_id = message_obj.create({'type' : 'email','subject' : "Hai",}).id
		mail_id = mail_obj.create({
                    'mail_message_id' : message_id,
                    # 'mail_server_id' : template.mail_server_id and template.mail_server_id.id or False,
                    'state' : 'outgoing',
                    # 'auto_delete' : template.auto_delete,
                    'email_to' : 'prasoon360@gmail.com',
                    
                    'body_html' : 'Any message in html',
                    }).id
		mail_obj.send(mail_id)


	

	user_id = fields.Many2one('res.users','Responsible', options={'no_open': True, 'no_create' :True})  #options is used here to hide the quick create thing 
	deadline = fields.Date('Deadline')
	name = fields.Char(help="What needs to be done ?")
	creator = fields.Char('Task created by')
	priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')],'Priority', default='1')
	# refers_to = fields.Reference([('res.users', 'User'), ('res.partner', 'Partner')],'Refers to')
	stage_id = fields.Many2one('todo.task.stage', 'Stage')
	tag_ids = fields.Many2many('todo.task.tag', 'Tags')
	stage_state = fields.Selection([('draft','Draft'),('started','Started'),('in_progress','In progress'),('done','Done')], 'Stage state',default="draft")
	user_todo_count = fields.Integer('User To-do count', compute='compute_user_todo_count')
	date = fields.Date('Date', default= lambda self: fields.Date.today(), readonly=True)
	desc = fields.Char(compute='onchange_desc', readonly=True)

	

	_sql_constraints = [('unique_name', 'UNIQUE(name,user_id)', 'Task title must be unique')]


	@api.one
	@api.constrains('user_id')
	def _check_user_id(self):
		print self.user_id
		if self.user_id.id == False:
			raise ValidationError("You must assign the task to a user")

	@api.one
	def toggle_done(self):
		if self.user_id != self.env.user:
			raise ValidationError('You cant do this')
		else:
			return super(TodoTask,self).toggle_done()


	@api.multi
	def clear(self):
		done_recs = self.search([('is_done', '=', 'True'),'|',('user_id','=',self.env.uid),('user_id','=',False)])
		done_recs.write({'active' : False})
		return True


	@api.depends('user_id')
	@api.multi
	def compute_user_todo_count(self):
		count=0
		for recs in self.search([]):
			if self.user_id.id == recs.user_id.id:
				count+=1
		self.user_todo_count = count



	@api.depends('user_id')
	@api.one
	def onchange_desc(self):
		if self.user_id:
			self.desc = self.user_id.name
			
	

	@api.one
	def set_started(self):
		self.write({'stage_state' : 'started' })


	@api.one
	def set_progress(self):
		if self.is_done == True:
			self.is_done = False
		self.write({'stage_state' : 'in_progress' })


	@api.one
	def set_done(self):
		self.write({'stage_state' : 'done', 'is_done' : True })




	@api.model
	def create(self, values):   #This function can be used instead of below create function 
		recs = self.env['res.users']
		userid = recs._uid
		values['creator'] = recs.browse([userid]).login
		self.email_task()
		res_id = super(TodoTask, self).create(values)
		return res_id


	

	# @api.cr_uid_context
	# def create(self, cr, uid, values, context=None):
	# 	if context is None:
	#             context = {}

	#         if context.get('tracking_disable'):
	#             return super(TodoTask, self).create(
	#                 cr, uid, values, context=context)

	#         # subscribe uid unless asked not to
	#         if not context.get('mail_create_nosubscribe'):
	#             pid = self.pool['res.users'].browse(cr, SUPERUSER_ID, uid).partner_id.id
	#             message_follower_ids = values.get('message_follower_ids') or []  # webclient can send None or False
	#             message_follower_ids.append([4, pid])
	#             values['message_follower_ids'] = message_follower_ids
	#             values['creator'] = self.pool.get('res.users').browse(cr,uid,uid,context=context).login #To display who created the task, edited my code

	#         thread_id = super(TodoTask, self).create(cr, uid, values, context=context)

	#         # automatic logging unless asked not to (mainly for various testing purpose)
	#         if not context.get('mail_create_nolog'):
	#             ir_model_pool = self.pool['ir.model']
	#             ids = ir_model_pool.search(cr, uid, [('model', '=', self._name)], context=context)
	#             name = ir_model_pool.read(cr, uid, ids, ['name'], context=context)[0]['name']
	#             self.message_post(cr, uid, thread_id, body=_('%s created') % name, context=context)

	#         # auto_subscribe: take values and defaults into account
	#         create_values = dict(values)
	#         for key, val in context.iteritems():
	#             if key.startswith('default_') and key[8:] not in create_values:
	#                 create_values[key[8:]] = val
	#         self.message_auto_subscribe(cr, uid, [thread_id], create_values.keys(), context=context, values=create_values)

	#         # track values
	#         track_ctx = dict(context)
	#         if 'lang' not in track_ctx:
	#             track_ctx['lang'] = self.pool.get('res.users').browse(cr, uid, uid, context=context).lang
	        

	#         if not context.get('mail_notrack'):
	#             tracked_fields = self._get_tracked_fields(cr, uid, values.keys(), context=track_ctx)
	#             if tracked_fields:
	#                 initial_values = {thread_id: dict.fromkeys(tracked_fields, False)}
	#                 self.message_track(cr, uid, [thread_id], tracked_fields, initial_values, context=track_ctx)

	#         return thread_id



