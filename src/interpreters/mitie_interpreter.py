from mitie import *

from rasa_nlu import Interpreter
from rasa_nlu.interpreters.mitie_interpreter_utils import get_entities
from rasa_nlu.tokenizers.mitie_tokenizer import MITIETokenizer


class MITIEInterpreter(Interpreter):
    @staticmethod
    def load(meta):
        """
        :type meta: ModelMetadata
        :rtype: MITIEInterpreter
        """
        if meta.entity_extractor_path:
            if meta.feature_extractor_path is None or not os.path.isfile(meta.feature_extractor_path):
                raise Exception("Invalid feature extractor path for MITIE model. Meta data: " + meta)
            extractor = named_entity_extractor(
                meta.entity_extractor_path, meta.feature_extractor_path)
        else:
            extractor = None
        if meta.intent_classifier_path:
            classifier = text_categorizer(
                meta.intent_classifier_path, meta.feature_extractor_path)
        else:
            classifier = None
        if meta.entity_synonyms_path:
            entity_synonyms = Interpreter.load_synonyms(meta.entity_synonyms_path)
        else:
            entity_synonyms = None
        return MITIEInterpreter(
            classifier,
            extractor,
            entity_synonyms)

    def __init__(self,
                 intent_classifier=None,
                 entity_extractor=None,
                 entity_synonyms=None):
        self.extractor = entity_extractor
        self.classifier = intent_classifier
        self.ent_synonyms = entity_synonyms
        self.tokenizer = MITIETokenizer()

    def get_intent(self, tokens):
        if self.classifier:
            label, score = self.classifier(tokens)
        else:
            label, score = "None", 0.0
        return label, score

    def parse(self, text):
        tokens = self.tokenizer.tokenize(text)
        intent, score = self.get_intent(tokens)
        entities = get_entities(text, tokens, self.extractor)
        if self.ent_synonyms:
            Interpreter.replace_synonyms(entities, self.ent_synonyms)

        return {'text': text, 'intent': intent, 'entities': entities, 'confidence': score}
