class CountVectorizer:
    """
    Векторизатор слов
    Получает на вход список строк,
    проходится по ним и создает one-hot вектора на
    их основе
    """

    def __init__(self):
        self.__corpus = list()


    def fit_transform(self, corpus: list):
        """
        Разбивает список строк на уникальные слова
        и составляет по нему corpus.

        Args:
            corpus(list): список строк для векторизации

        Returns:
            list: матрица векторов каждой строки из введенного списка

        Raises:
            ValueError: В случае, если передан не единообразный список строк
        """
        if not isinstance(corpus, list):
            raise ValueError("Введен не список")

        self.__corpus = list()

        for sentance in corpus:

            if not isinstance(sentance, str):
                raise ValueError("Введен не список строк")

            for word in sentance.lower().split(" "):
                if word not in self.__corpus:
                    self.__corpus.append(word)

        count_matrix = []

        for element in corpus:
            count_matrix.append([0 for _ in range(len(self.__corpus))])
            for word in element.lower().split(" "):
                count_matrix[-1][self.__corpus.index(word)] += 1

        return count_matrix


    def get_feature_names(self):
        return self.__corpus


if __name__ == "__main__":
    corpus = [
        "Crock Pot Pasta Never boil pasta again",
        "Pasta Pomodoro Fresh ingredients Parmesan to taste",
    ]

    vectorizer = CountVectorizer()
    count_matrix = vectorizer.fit_transform(corpus)
    print(vectorizer.get_feature_names())
    print(count_matrix)
