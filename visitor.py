# -*- coding: utf-8 -*-


class Visitor:
    def visit(self, manager):
        self.begin_visit(manager)
        manager.visit(self)
        return self.end_visit(manager)

    def begin_visit(self, manager):
        pass

    def end_visit(self, manager):
        pass

    def begin_chapter(self, chapter):
        pass

    def end_chapter(self, chapter):
        pass

    def begin_section(self, section, chapter):
        pass

    def end_section(self, section, chapter):
        pass

    def visit_talk(self, talk, section, chapter):
        pass
