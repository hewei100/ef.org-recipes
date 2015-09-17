#!/usr/bin/env python

import urllib2
import xml.dom.minidom

from autopkglib import Processor, ProcessorError

__all__ = ["MunkiToolsAdminRemover"]

class MunkiToolsAdminRemover(Processor):
    description = "Remove admin sub-package from the distribution file"
    input_variables = {
        "distribution_file": {
            "required": True,
            "description": "Path to the distribution file."
        }
    }
    output_variables = {
        "core_version": {
            "description": "The version number of the core sub-package."
        }
    }

    __doc__ = description

    def main(self):

        distribution_file = self.env['distribution_file']

        try:
            the_xml = xml.dom.minidom.parse(distribution_file)
        except BaseException as e:
            raise ProcessorError("Cannot open munkitools destribution file: '%s'" % distribution_file)

        root = the_xml.documentElement
        choice_outline = root.getElementsByTagName('choices-outline')[0]
        lines = choice_outline.getElementsByTagName('line')
        for c in lines:
            if c.getAttribute('choice') == 'admin':
                choice_outline.removeChild(c)

        choices = root.getElementsByTagName('choice')
        for c in choices:
            if c.getAttribute('id') == 'admin':
                root.removeChild(c)
                

        pkg_refs = root.getElementsByTagName('pkg-ref')
        for c in pkg_refs:
            if c.getAttribute('id') == 'com.googlecode.munki.admin':
                root.removeChild(c)
            elif c.hasAttribute('version') and c.getAttribute('id') == 'com.googlecode.munki.core':
                version = c.getAttribute('version')
                self.output("Found munki core version %s." % version)
                self.env['core_version'] = version

        f = open(distribution_file, 'w')
        f.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?>' + "\n")
        f.write(root.toxml('utf-8'))
        f.close()
        self.output("Modifed %s with admin sub-package removed." % distribution_file)

if __name__ == "__main__":
    processor = MunkiToolsAdminRemover()
    processor.execute_shell()
