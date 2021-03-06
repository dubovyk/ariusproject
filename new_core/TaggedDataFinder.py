import os
from AbstractDataFinder import AbstractDataFinder
from DifflibMatchFinder import DifflibMatchFinder
from FuzzyMatchFinder import FuzzyMatchFinder
from tinydb import TinyDB, Query
from Result import Result
import sys
sys.path.append("../")
from config import config


class TaggedDataFinder(AbstractDataFinder):
    """
    This DataFinder is used to work with TinyDB database
    and returns search results from pretagged data.

    It returns a list of Result instances with
    body equal to path, and type qualt to extension.
    """

    def __init__(self, query_generator, output_processor, database):
        super(TaggedDataFinder, self).__init__(query_generator, output_processor)
        self.__db = TinyDB(database)
        self.__tags = self.__db.table('tag_data')
        self.__synonyms = self.__db.table('synonyms')

    def getRawResult(self, keywords):
        result = []
        # replace synonyms by keys
        keywords = self.get_keys_by_synonyms(keywords)
        data = self.__tags.all()
        for d in data:
            entry_tags = self.get_tags(d)
            conf = self.get_confidence(entry_tags, keywords)
            if conf > 0:
                result.append(Entry(d['name'], d['path'], float(d['priority']), conf))
        if result:
            result = sorted(result, key=lambda s: (s.confidence, - s.priority), reverse=True)
            return [Result(r.path, os.path.splitext(r.path)[1]) for r in result]
            # return [(r.path, r.priority, r.confidence) for r in result]
        return None

    def get_tags(self, data_entry):
        res = [(t[0].lower(), t[1]) for t in data_entry['tags']]
        return res

    def __is_in(self, string1, string2):
        confidence = DifflibMatchFinder.getMatch(string1.lower(), string2.lower())
        if confidence > config['core_tag_search_min_confidence']:
            return True
        return False

    def get_confidence(self, entry_tags, keywords):
        res = 0
        for keyword in keywords:
            for tag in entry_tags:
                if self.__is_in(tag[0], keyword):
                    # if keyword.lower() in [tag[0].lower() for tag in entry_tags]:
                    res += float(tag[1])
        return res

    def get_keys_by_synonyms(self, tags):
        keys = []
        for tag in tags:
            keys += self.get_keys_by_synonym(tag)
        return list(set(keys))

    def get_keys_by_synonym(self, keyword):
        data = self.__synonyms.all()
        result = set()
        for synonym in data:
            for word in synonym['equal']:
                if self.__is_in(keyword, word):
                    result.add(synonym['key'])
                    break
        return list(result)


class Entry:
    def __init__(self, name, path, priority, confidence):
        self.name = name
        self.path = path
        self.confidence = confidence
        self.priority = priority

if __name__ == '__main__':
    from KeywordsQueryGenerator import KeywordsQueryGenerator
    from NoModifyingDataFinderOutputProcessor import NoModifyingDataFinderOutputProcessor
    t = TaggedDataFinder(KeywordsQueryGenerator(), NoModifyingDataFinderOutputProcessor(), config['database_file'])
    print(t.getRawResult(['mylkos']))