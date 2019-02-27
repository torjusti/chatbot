from model.ModelFactory import ModelFactory
import model.db_util as util
from sklearn.metrics.pairwise import cosine_similarity
from model.keyword_gen import get_tfidf_model


class MongoDBControllerWebhook:
    """
    This class should be between the dialogflow API and the MongoDB (model).
    It should handle when a user asks a question.
    """

    def webhook_query(self, raw_query_text, intent, entities, default_text):
        """
        Called when a user asks a question.
        dialogflow --> Flask --> Controller --> model --> controller -->
        flask --> dialogflow

        :param raw_query_text: This is the full query text from the user.
        :param intent: The intent that got automatically matched.
        :param entities: The entities that got matched.
        :param default_text: The randomly chosen static reply if the intent
        has any.

        :return: This should just return a simple string.
        """
        print("raw_query_text:", raw_query_text)
        print("intent:", intent)
        print("entities:", entities)
        print("default_text:", default_text)

        # Connect to database to retrieve documents
        factory = ModelFactory.get_instance()
        util.set_db(factory, db="dev_db")

        docs = factory.get_document(raw_query_text, "dev")

        def get_corpus_text(doc):
            content = ' '.join(doc['content']['texts'])
            return doc['content']['title'] + ' ' + content

        def get_answer_text(doc):
            content = ' '.join(doc['content']['texts']) + '\n' + doc['url']
            return doc['content']['title'] + ':\n' + content

        corpus = [get_corpus_text(doc) for doc in docs]
        vectorizer, corpus_matrix, feature_names = get_tfidf_model(corpus)

        try:
            scores = cosine_similarity(vectorizer.transform([raw_query_text]), corpus_matrix)[0]
            answer = get_answer_text(docs[scores.tolist().index(max(scores))])
            print("Answer:", answer)
            return answer
        except KeyError:
            raise Exception("Document doesn't have content and texts. "
                            "Unable to retrieve text from document in dbcontroller webhook")
        except ValueError:
            return "Jeg fant ikke informasjonen du spurte etter."
