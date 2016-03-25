from openerp import fields,api,models


class Tag(models.Model):
	_name = 'todo.task.tag'
	task_ids = fields.Many2many('todo.task', string='Tasks')