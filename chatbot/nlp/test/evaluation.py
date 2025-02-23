import json
from chatbot.nlp.query import _perform_search


def evaluate_test(test):
    """
    :param test: a dictionary containing a question key and answers key.
    :return: A score between 0 and 1.
    """
    questions = test["question"]
    # A score for all the questions
    score = 0
    # How many questions
    n_questions = len(questions)
    # How many of the questions gave the correct url
    url_score = 0

    for question in questions:
        # The answer our system gave.
        our_answer = _perform_search(question)
        # The score for this specific question.
        score_question = 0
        score_url = 0
        for correct_url in test["urls"]:
            if correct_url in our_answer:
                score_url = 1
        if score_url == 0:
            print("\nOur answer was", our_answer)
            print("\nCorrect URL was", test["urls"])
        url_score += score_url

        correct_answers = test["answers"]
        for correct_answer in correct_answers:
            if correct_answer["text"] in our_answer:
                # Max here, because the maximum score for score_question should
                # be 1.
                score_question = max(score_question, correct_answer["score"])
        score += score_question

        if score_question < 1:
            print("Question:\n", question)
            print()
            print("Gave:\n", our_answer)
            print()
            print("Correct:\n", correct_answers)
            print("\n\n\n\n")

    return n_questions, score, url_score


def main():
    f = open("chatbot/nlp/test/test_data/test_data_evaluation.json")
    raw_file = f.read()
    f.close()
    tests = json.loads(raw_file)

    n_questions = 0
    score = 0
    url_score = 0

    for test in tests:
        partial_n, partial_score, partial_url = evaluate_test(test)
        n_questions += partial_n
        score += partial_score
        url_score += partial_url

    print("Number of questions:", n_questions,
          "score:", score,
          "URLs correct:", url_score)

    print("Text Precision:", score / n_questions)
    print("URL Precision:", url_score / n_questions)


if __name__ == '__main__':
    main()
