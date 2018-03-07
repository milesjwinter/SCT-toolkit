from __future__ import absolute_import
import os, sys
import imp

class docs(object):
    def __init__(self, show=True, update=False):
        """ 
        Class for viewing and building documentation 

        Parameters
        ----------
        show : bool
            If True, show docs after rebuilding (default: True)
        update : bool
            If True, rebuild documentation to reflect code changes (default:True)

        """
        self.build_path = '/'.join(imp.find_module('sct_toolkit')[1].split('/')[:-1])+'/docs'
        self.source_path = self.build_path+'/_build/html/index.html'
        if update:
            self._update_docs()
        if show:
            self._show_docs()

    def _show_docs(self):
        """ Launch documentation in web browser """
        try:
            if sys.platform == 'darwin':
                os.system('open {}'.format(self.source_path))
            else:
                os.system('open-xdg {}'.format(self.source_path))
        except IOError:
            raise IOError("documentation file '{}' could not be opened".format(self.source_path))

    def _update_docs(self):
        """ Rebuild documentation """
        os.system('make -C {} html'.format(self.build_path))
