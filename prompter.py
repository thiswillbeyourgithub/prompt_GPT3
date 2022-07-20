from pathlib import Path
import openai
import time
import logging
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


### SETTINGS #####################################
default_t = 0.1
maximum_tokens = 2000
default_language = "english"
default_translation = "french_to_argentinian"
default_mode = "freewriting"

### VARIABLES ####################################
local_dir = "/".join(__file__.split("/")[:-1])
openai.api_key = str(Path(f"{local_dir}/API_KEY.txt").read_text()).strip()
possible_modes = ["freewriting", "cloze", "translate"]
cloze_prompts = {
    "english": "Q: In what year was Napoleon born?\nA: {{c1::Napoleon was born in 1769}}\n\nQ: 1+1?\nA: {{c1::1+1 equals 2}}\n\nQ: Capital of France?\nA: {{c1::Paris is the capital of France}}\n\nQ: ",
    "french": "Q: Année de naissance de Napoléon ?\nA: {{c1::Napoléon est né en 1769}}\n\nQ: 1+1 ?\nA: {{c1::1+1 vaut 2}}\n\nQ: Capitale de la France ?\nA: {{c1::Paris est la capitale de la France}}\n\nQ: "
    }
translate_prompts = {
        "english_to_argentinian": "Translate this sentence to argentinian: '",
        "french_to_argentinian": "Traduit cette phrase en argentin: '"
        }
        

##################################################

def ask_user(q, completer_list=None, dont_catch=False):
    "prompt user but catch keyboard interruption"
    autocomplete = WordCompleter(completer_list, match_middle=True, ignore_case=True) if completer_list else None
    try:
        return prompt(q, completer=autocomplete)
    except (KeyboardInterrupt, EOFError):
        if dont_catch:
            raise KeyboardInterrupt  # this way, ctrl+c can be used either to
        # terminate the script if in the outer loop or to break the inner
        # while loop
        else:
            raise SystemExit()


if __name__ == "__main__":
    Path(f"{local_dir}/logs.txt").touch(exist_ok=True)
    logging.basicConfig(filename=f"{local_dir}/logs.txt",
                    filemode='a',
                    format=f"{time.asctime()}: %(message)s")
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    language = None
    trans_lan = None
    assert default_translation in translate_prompts.keys(), f"Wrong default translation value: {default_translation}"
    assert isinstance(default_t, float) and default_t <= 1 and default_t >= 0, f"Wrong default temperature value: {default_t}"
    assert default_language in cloze_prompts.keys(), f"Wrong default value for language: {default_language}"

    loaded_logs = Path(f"{local_dir}/logs.txt").read_text().split("\n")
    previous_questions = []
    for line in loaded_logs:
        if " Q: " in line:
            inc = 0
            while inc < len(line):
                inc+=1
                if line[inc:].startswith(" Q: "):
                    candidate = line[inc+4:]
                    if candidate not in previous_questions and candidate.strip() not in previous_questions and candidate != "":
                        previous_questions.insert(0, candidate)
                    break
    if previous_questions:
        print(f"Loaded {len(previous_questions)} previous questions from logs.txt")
    previous_questions.reverse()

    while True:
        # choose a temperature
        t = ask_user(f"Temperature settings? (0 to 1)\n>")
        if t == "":
            print(f"Temperature set to {default_t}\n")
            t = default_t
        else:
            try:
                t = float(t)
            except Exception:
                pass
        assert isinstance(t, float), f"Wrong value for temperature: {t}"
        assert t <= 1 and t >= 0, f"Wrong value for temperature: must be between 0 and 1"

        # choose a mode
        mode = ask_user(f"Mode ? ({', '.join(possible_modes)})\n>", possible_modes)
        if mode == "":
            print(f"Mode set to {default_mode}\n")
            mode = default_mode
        assert mode in possible_modes

        if mode == "cloze":
            # chose a language
            possible_cloze_languages = cloze_prompts.keys()
            language = ask_user(f"Language? ({', '.join(possible_cloze_languages)})\n>", possible_cloze_languages)
            if language == "":
                print(f"Language set to {default_language}\n")
                language = default_language
            assert language in possible_cloze_languages, f"Wrong value for language: {language}"
        elif mode == "translate":
            # chose a language
            possible_translation = translate_prompts.keys()
            trans_lan = ask_user(f"Language? ({', '.join(possible_translation)})\n>", possible_translation)
            if trans_lan == "":
                print(f"Language set to {default_translation}\n")
                trans_lan = default_translation
            assert trans_lan in possible_translation, f"Wrong value for translation: {trans_lan}"

        log.info(f"\n\nNew session: T={t} ; Mode={mode} ; Language={language} ; Translation={trans_lan}")

        print("\n(Press ctrl+c to go edit settings, again to exit)\n")

        while True:
            try:
                question = ask_user("\n\nWhat's your question?\n> ", previous_questions, True).strip()
            except KeyboardInterrupt:
                print("\n"*3)
                break

            if mode == "cloze":
                if not question.endswith("?"):
                    # correct space location for question mark
                    if language == "french":
                        question += " ?"
                    else:
                        question += "?"
                # makes sure to have a first letter be uppercase
                question = question[0].upper() + question[1:]
                previous_questions.append(question)
                p = cloze_prompts[language] + question + "\nA:"
            elif mode == "translate":
                question = question[0].upper() + question[1:]
                p = translate_prompts[trans_lan] + question + "'"
            else:
                p = question
                previous_questions.append(p)

            try:
                response = openai.Completion.create(engine="text-davinci-002",
                                                    prompt=p,
                                                    temperature=t,
                                                    max_tokens=maximum_tokens,
                                                    top_p=1,
                                                    ##############################################
                                                    ##### DO NOT CHANGE THE VALUE BEST_OF PLEASE #
                                                    best_of=1, ###################################
                                                    ##### DO NOT CHANGE THE VALUE BEST_OF PLEASE #
                                                    ##############################################
                                                    frequency_penalty=0.5,
                                                    presence_penalty=0.6
                                                    )
            except KeyboardInterrupt:
                print("Exit.")
                raise SystemExit()

            print("\n" + "#" * 20)

            if question == "":
                print("Empty question.")
                continue
            else:
                try:
                    print(question)
                    ans = str(response["choices"][0]["text"]).strip()
                    print(ans)
                    log.info(f"Q: {question}")
                    log.info(f"A: {ans}")
                    print("#" * 20 + "\n")
                except Exception as e:
                    print(f"Error : {str(e)}")
                    breakpoint()
