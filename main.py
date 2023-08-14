import json
from difflib import get_close_matches
import requests
from bs4 import BeautifulSoup

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data;

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_questions: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_questions, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledgeBase: dict) -> str | None:
    for t in knowledgeBase["topics"]:
        if t["topic"] == question:
            return t["answer"]


def scrape_topic_information(topic: str) -> str | None:
    url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract relevant information from the page, adjust the specific selectors as needed
        main_content = soup.find('div', {'id': 'mw-content-text'})
        paragraphs = main_content.find_all('p')
        article_text = '\n'.join([p.get_text() for p in paragraphs])
        return article_text
    else:
        return None

def chat_bot():
    knowledgeBase: dict = load_knowledge_base('knowledgeBase.json')

    while True:
        print('Bot: Enter a topic you\'d like to learn about or type "quit" to terminate the program')
        user_input: str = input('You: ')

        if user_input.lower() == 'quit':
            break

        best_match: str | None = find_best_match(user_input, [t["topic"] for t in knowledgeBase["topics"]])

        if best_match:
            answer: str = get_answer_for_question(best_match, knowledgeBase)
            print(f'Bot: {answer}')
        else:
            print('Bot: I don\'t know anything on the subject. Would you like me to research it?')
            new_answer: str = input('Type anything to research or "skip" to skip: ')

            if new_answer.lower() != 'skip':

                scraped_text = scrape_topic_information(user_input)
                if scraped_text:
                    print(f'Bot: Here is some information I found:\n{scraped_text}')
                    knowledgeBase["topics"].append({"topic": user_input, "answer": scraped_text})
                    save_knowledge_base('knowledgeBase.json', knowledgeBase)
                    print('Bot: I\'ve logged this information for the next time you ask!')
                else:
                    print('Bot: I couldn\'t find information on that topic.')

if __name__ == '__main__':
    chat_bot()