# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.dp import Action
try:
    from ncs.experimental import Subscriber
except ImportError:
    from ncs.cdb import Subscriber
from time import strftime


class GenerateLoopupFile(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output, trans):
        self.log.info('action name: ', name)
        result = ''
        output.result = result


class UpdateSubscriber(Subscriber):
    def init(self):
        self.register('/csm-lookup:csm-lookup/csm-lookup:device-to-service', priority=100)

    # Initate your local state
    def pre_iterate(self):
        return []

    # Iterate over the change set
    def iterate(self, keypath, op, oldval, newval, state):
        self.log.info('Subscriber kp: ' + str(keypath))
        updated = True
        state.append(updated)
        return ncs.ITER_RECURSE

    # This will run in a separate thread to avoid a transaction deadlock
    def post_iterate(self, state):
        self.log.info('Updateubscriber: post_iterate, state=', state)
        with ncs.maapi.single_write_trans('system', 'system') as trans:
            csm_lookup = ncs.maagic.get_node(trans, '/csm-lookup:csm-lookup')
            csm_lookup.last_modified = strftime("%Y-%m-%d %H:%M:%S")
            trans.apply()

    # determine if post_iterate() should run
    def should_post_iterate(self, state):
        return state != []


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')
        self.register_action('lookup-action', GenerateLoopupFile)
        self.sub = UpdateSubscriber(app=self)
        self.sub.start()

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.
        self.sub.stop()
        self.log.info('Main FINISHED')
