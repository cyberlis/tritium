"""
tritium -- a window manager inspired by tuomo
Copyright 2007 Mike O'Connor <stew@vireo.org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

__distname__ = 'tritium'
__version__ = '0.3.7'
__description__ = 'a tabbed/tiling window manager'
__long_description__ = \
"""
tritium is a tiling/tabbed window manager for the X Window System
inspired by the ion window manager.  It was written completely from
scratch in Python and shares no actual code with ion.

tritium is implemented in Python using the plwm ("pointless window
manager") library, which is available here:
 	http://plwm.sourceforge.net
"""

__author__ = "Mike O'Connor"
__email__ = 'stew@vireo.org'
__url__ = 'http://tritium.vireo.org/'
__license__ = 'GPL'

import logging
from Xlib import X
from plwm import wmanager, wmevents, modewindow
from workspace import Workspace
from frame.frame import Frame
from cycle import Cycle
import query
import traceback

log = logging.getLogger()

class tritiumScreen(object):
    "tritium mixin for Screens."

    def  __screen_client_init__( self ):
        log.debug( "tritiumScreen. __screen_client_init__" )
        "Create the initial pane object for this screen."
        wmanager.debug( 'panesScreen', 'Initializing screen %d', self.number )
        self.dispatch.add_handler( X.ConfigureRequest, self.configure_frame )
#        ws = self.wm.new_floating_workspace( self )
#        ws = self.wm.new_workspace( self )

    def configure_frame( self, event ):
        w = self.get_window( event.window )
        if w:
            if event.value_mask & (X.CWX | X.CWY | X.CWWidth | X.CWHeight):
                if w.frame:
                    w.frame.place_window( w )

            if event.value_mask & X.CWStackMode and event.stack_mode == X.Above \
               and self.allow_self_changes( w ):
                if w.frame:
                    w.frame.place_window( w )

    def maximize_frame( self, frame ):
        "Make the pane use the all the available screen."

        # todo, make root for a toolbar/statusbar?
        frame.x = 0
        frame.y = 0
        frame.width = self.root_width
        frame.height = self.root_height

class tritiumWindowManager(object):
    """
    tritium window manager mixin
    """
    def __wm_init__( self ):
        "Enable activation, then activate the first pane."
        
        log.debug( "tritiumWindowManager.__wm_init__" )
        self.runCommand = query.runCommand()
        self.runCommandInXterm = query.runCommandInXterm()
        self.runSSH = query.runSSH()
        self.runPython = query.runPython()
        self.runMan = query.runMan()
        
    #TODO: figure out what this is all about:
        Frame.activate = Frame._activate

    class actions_menu(object):
        def __init__( self, client ):
            width, height = client.screen.menu_make( [ 'close', client.delete ] )
                    
            pass
        def __call__( self, choice ):
            pass

    class appmenu(object):
        "Creates a menu of applications to run in a pane."

        def __init__( self, wm, apps ):
            "Create and run the applications menu from the keys."

            frame = wm.current_frame()
            labels = apps.keys()
            labels.sort()
            width, height = frame.screen.menu_make(labels)
            self.wm = wm
            self.system = frame.screen.system
            self.apps = apps
            frame.screen.menu_run( ( frame.width - width ) / 2 + frame.x,
                                   ( frame.height - height ) / 2 + frame.y,
                                   self )

        def __call__(self, choice):
            "Call the system function on the value of the given choice."

            exec self.apps[choice] in {'wm':self.wm}

