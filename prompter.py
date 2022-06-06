from pathlib import Path
import openai

### SETTINGS #####################################
default_t = 0.1
default_language = "french"
default_mode = "cloze"
openai.api_key = str(Path("API_KEY.txt").read_text()).strip()

cloze_prompts = {
    "english": "Q: In what year was Napoleon born?\nA: {{c1::Napoleon was born in 1769}}\n\nQ: 1+1?\nA: {{c1::1+1 equals 2}}\n\nQ: Capital of France?\nA: {{c1::Paris is the capital of France}}\n\nQ: ",
    "french": "Q: Année de naissance de Napoléon ?\nA: {{c1::Napoléon est né en 1769}}\n\nQ: 1+1 ?\nA: {{c1::1+1 vaut 2}}\n\nQ: Capitale de la France ?\nA: {{c1::Paris est la capitale de la France}}\n\nQ: "
    }

##################################################

def input2(prompt):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        raise SystemExit()


if __name__ == "__main__":
    while True:
        # choose a temperature
        t = input2(f"Temperature settings? (0 to 1)\n>")
        if t == "":
            print(f"Temperature set to {default_t}\n")
            t = default_t
        try:
            t = float(t)
        except Exception:
            pass
        assert isinstance(t, float), f"Wrong value for temperature: {t}"
        assert t <= 1 and t >= 0, f"Wrong value for temperature: must be between 0 and 1"

        # choose a mode
        mode = input2("Mode ? (freewriting / cloze)\n>")
        if mode == "":
            print(f"Mode set to {default_mode}\n")
            mode = default_mode
        assert mode.startswith("f") or mode.startswith("c"), f"Wrong value for mode: {mode}"
        if mode.startswith("f"):
            mode = "freewriting"
        elif mode.startswith("c"):
            mode = "cloze"

        if mode == "cloze":
            # chose a language
            language = input2("Language? (english / french)\n>")
            if language == "":
                print(f"Set default language to {default_language}\n")
                language = default_language
            if language.startswith("e"):
                language = "english"
            elif language.startswith("f"):
                language = "french"
            else:
                raise SystemExit(f"Wrong value for language: {language}")
        else:
            language = None

        while True:
            try:
                question = input("\n\nWhat's your question? (ctrl+c to restart)  > ").strip()
            except KeyboardInterrupt:
                print("\n"*3)
                break

            if mode == "freewriting":
                p = question
            elif mode == "cloze":
                if not question.endswith("?"):
                    if language == "french":
                        question += " ?"
                    elif language == "english":
                        question += "?"
                question = question[0].upper() + question[1:]
                p = cloze_prompts[language] + question + "\nA:",

            response = openai.Completion.create(engine="text-davinci-002",
                                                prompt=p,
                                                temperature=t,
                                                max_tokens=2000,
                                                top_p=1,
                                                ##############################################
                                                ##### DO NOT CHANGE THE VALUE BEST_OF PLEASE #
                                                best_of=1, ###################################
                                                ##### DO NOT CHANGE THE VALUE BEST_OF PLEASE #
                                                ##############################################
                                                frequency_penalty=0.1,
                                                presence_penalty=0.6
                                                )
            print("\n" + "#" * 20)

            if question == "":
                print("Empty question.")
                continue
            else:
                try:
                    print(question)
                    print(str(response["choices"][0]["text"]).strip())
                    print("#" * 20 + "\n")
                except Exception as e:
                    print(f"Error : {str(e)}")
                    breakpoint()
