import time
import types

from copy import deepcopy

from .scrape_operations import ScrapeOp, ClickOp, ReadOp, WriteOp, ScrollOp, KeyOp

class CommonActions():

    OpenPage = lambda url: Action(f'open_url', url, None, None)
    Scroll = lambda name: Action(name, None, None, ScrollOp())
    Wait = lambda name, sleeptime: Action(name, None, None, lambda: time.sleep(sleeptime))

class Action():

    name = None 
    start = None,
    target_xpath = None
    op = None
    args = None

    output = None
    out_op = None

    scraper = None

    def __init__(self, name, start, target_xpath, op, args=None, out_op=None):
        self.name = name
        self.start = start
        self.target_xpath = target_xpath
        self.op = op
        self.args = args
        self.out_op = out_op

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return f"""
            name: {self.name},
            start: {self.start},
            target: {self.target_xpath},
            op: {self.op}
        """

    def run(self):
        print(f'run action: {self.name}')
        self._start_action()
        self._eval_target_path()
        self._exec_op()
        self._compute_output()

    def _start_action(self):
        if self.start != None:
            self._eval_start()
            self.scraper.open_page(self.start)

    def _eval_start(self):
        if isinstance(self.start, types.FunctionType):
            self.start = self.start(**self.args) if self.args != None else self.start()

    def _eval_target_path(self):
        if self.target_xpath != None:
            if isinstance(self.target_xpath, types.FunctionType):
                self.target_xpath = self.target_xpath(**self.args) if self.args != None else self.target_xpath()

    def _exec_op(self):
        if self.op != None:
            self._compute_args()
            self._build_op()
            self.output = self.op(**self.args) if self.args != None else self.op()
    
    def _compute_output(self):
        if self.out_op != None:
            self.output = self.out_op(self.output)

    def add_arg(self, kwargs):
        if self.args != None:
            personal_args = deepcopy(self.args)
            # self.args = lambda: [arg, personal_args() if isinstance(personal_args, types.FunctionType) else personal_args]
            self.args = lambda: {**kwargs, **(personal_args() if isinstance(personal_args, types.FunctionType) else personal_args)}
        else:
            self.args = kwargs

    def _compute_args(self):
        if isinstance(self.args, types.FunctionType):
            self.args = self.args()
        
    def _build_op(self):
        if isinstance(self.op, ScrapeOp):
            self.op.scraper = self.scraper
            self.op.xpath = self.target_xpath

    def clone(self):
        cloned = Action(self.name, self.start, self.target_xpath, self.op, self.args, self.out_op)
        cloned.scraper = self.scraper
        return cloned
       
class Procedure(dict):

    name = None
    actions = None
    args = None
    
    output = None
    out_op = None

    def __init__(self, name, action_list, args=None, out_op=None):
        self.name = name
        self.actions = {action.name: action for action in action_list}
        self.args = args
        self.out_op = out_op

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return f"""
            name: {self.name},
            actions: {self.actions}
        """

    def __getitem__(self, __key):
        return self.actions[__key]
    
    def __setitem__(self, __key, __value):
        self.actions[__key] = __value

    def add_action(self, action):
        self.actions[action.name] = action
        return self

    def action_list(self):
        return [action for action in self.actions.values()]
    
    def run(self):
        self._compute_args()
        for action_index, action in enumerate(self.action_list()):
            action.run()
        self._compute_output()

    def add_arg(self, kwargs):
        if self.args != None:
            personal_args = deepcopy(self.args)
            #self.args = lambda: [arg, personal_args() if isinstance(personal_args, types.FunctionType) else personal_args]
            self.args = lambda: {**kwargs, **(personal_args() if isinstance(personal_args, types.FunctionType) else personal_args)}
        else:
            self.args = kwargs

    def _compute_args(self):
        if isinstance(self.args, types.FunctionType):
            self.args = self.args()        
        for action_index, action in enumerate(self.action_list()):
            action.add_arg(self.args)

    def _compute_output(self):
        output = {}
        for action_name, action in self.actions.items():
            if isinstance(action, Procedure):
                action._compute_output()
            output[action_name] = action.output
        self.output = self.out_op(output) if self.out_op != None else output

    def clone(self):
        cloned = Procedure(self.name, [subprocedure.clone() for subprocedure in self.action_list()], self.args, self.out_op)
        cloned.output = self.output
        return cloned

class Iterated(Procedure):

    action = None
    current_iteration = 0
    current_action = None
    iter_args = None

    out_op = None

    def __init__(self, action, times, iter_args=None, out_op=None):
        super().__init__(action.name, [])
        self.action = action
        self.times = times
        self.iter_args = iter_args

    def __getitem__(self, __key):
        return self.actions[__key]    
    def __setitem__(self, __key, __value):
        self.actions[__key] = __value

    def run(self):
        self._compute_times()
        self._compute_iter_args()
        for it in range(self.times):
            self._run_iteration(it)
        self._compute_output()

    def _run_iteration(self, iteration_number):
        self.current_iteration = iteration_number
        self._evaluate_current_action()
        self.current_action.run()    

    def _evaluate_current_action(self):
        self.current_action = self.action.clone()
        self.current_action.name = f'{self.action.name}_{self.current_iteration}'
        self._set_current_iter_args()
        self.actions[self.current_action.name] = self.current_action

    def _compute_times(self):
        if isinstance(self.times, types.FunctionType):
            self.times = self.times()

    def _compute_iter_args(self):
        if isinstance(self.iter_args, types.FunctionType):
            self.iter_args = self.iter_args()

    def _set_current_iter_args(self):
        if self.iter_args != None:
            # if self.current_action.args != None:
            #     self.current_action.args = lambda: [self.iter_args[self.current_iteration], self.current_action._compute_args()]
            # else:
            #     self.current_action.args = self.iter_args[self.current_iteration]
            self.current_action.add_arg(self.iter_args[self.current_iteration])

    def _compute_output(self):
        output = []
        for action_name, action in self.actions.items():
            if isinstance(action, Iterated):
                action._compute_output()
            output.append(action.output)
        self.output = self.out_op(output) if self.out_op != None else output
        

    def clone(self):
        return Iterated(self.action.clone(), self.times)