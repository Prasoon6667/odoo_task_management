from openerp import fields,api,models

class Stage(models.Model):
	_name = 'todo.task.stage'

	tasks = fields.One2many('todo.task','stage_id',string='Tasks in this stage')