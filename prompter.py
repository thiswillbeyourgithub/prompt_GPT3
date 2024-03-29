#!/usr/bin/python3

import json
import fire
from pathlib import Path
import openai
import time
import logging
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


# VARIABLES AND PROMPTS ########################
possible_modes = ["freewriting", "cloze", "translate", "paragraph_cloze"]
paragraph_cloze = {
        "parser": "Texte: Napoléon est né en 1769 à Ajaccio. Il est connu en tant que premier empereur des Français.\nStructure: Napoléon est (q1:né en 1769) (q2:à Ajaccio). Il est (q3:connu en tant que premier empereur des Français).\n\n Texte: Le pancréas est situé dans la partie postérieure de la cavité abdominale, devant le rachis et les organes rétropéritonéaux. Il est en majeure partie fixe, accolé en arrière par des fascias.\nStructure: Le pancréas est (q1:situé dans la partie postérieure de la cavité abdominale), (q2:devant le rachis et les organes rétropéritonéaux). Il (q3:est en majeure partie fixe), (q4:accolé en arrière) (q5:par des fascias).\n\nTexte: ",
        "clozer": "Texte: Napoléon est (q1:né en 1769) (q2:à Ajaccio).\nQuestion1: Napoléon, date de naissance ?<br>{{cc1::1769}}\nQuestion2: Napoléon, lieu de naissance ?<br>{{cc1::Ajaccio}}\n\nTexte: "
        }
cloze_prompts = {
    "english": "Q: In what year was Napoleon born?\nA: {{c1::Napoleon was born in 1769}}\n\nQ: 1+1?\nA: {{c1::1+1 equals 2}}\n\nQ: Capital of France?\nA: {{c1::Paris is the capital of France}}\n\nQ: ",
    "french": "Q: Année de naissance de Napoléon ?\nA: {{c1::Napoléon est né en 1769}}\n\nQ: 1+1 ?\nA: {{c1::1+1 vaut 2}}\n\nQ: Capitale de la France ?\nA: {{c1::Paris est la capitale de la France}}\n\nQ: "
    }
translate_prompts = {
        "english_to_argentinian": "Translate this sentence to argentinian: '",
        "french_to_argentinian": "Traduit cette phrase en argentin: '"
        }

##################################################


def ask_user(q,
             completer_list=None,
             dont_catch=False,
             vi_mode=False,
             multiline=False):
    "prompt user but catch keyboard interruption"
    autocomplete = WordCompleter(completer_list,
                                 match_middle=True,
                                 ignore_case=True) if completer_list else None
    try:
        return prompt(q,
                      completer=autocomplete,
                      vi_mode=vi_mode,
                      multiline=multiline)
    except (KeyboardInterrupt, EOFError):
        if dont_catch:
            raise KeyboardInterrupt  # this way, ctrl+c can be used either to
        # terminate the script if in the outer loop or to break the inner
        # while loop
        else:
            raise SystemExit()


def ask_gpt(p, t, maximum_tokens):
    "sends the prompt to openAI"
    return openai.Completion.create(
            engine="text-davinci-003",
            # engine="text-curie-001",
            prompt=p,
            temperature=t,
            max_tokens=maximum_tokens,
            top_p=1,
            ##############################################
            ##### DO NOT CHANGE THE VALUE BEST_OF PLEASE #
            best_of=1, ###################################
            ##### DO NOT CHANGE THE VALUE BEST_OF PLEASE #
            ##############################################
            frequency_penalty=0,
            presence_penalty=0,
            )


def run(credentials_path="API_KEY.txt",
        vi_mode=True,
        default_temperature=0.1,
        maximum_tokens=4000,
        default_language="english",
        default_translation="french_to_argentinian",
        default_mode="freewriting",
        ):
    """
    Simple GPT3 prompter. Add your credentials to a file called 'API_KEY.txt"
    and everything should work out of the box. Users other than the author
    will probably not care about other modes than 'freewriting' and should
    ignore them.
    """
    local_dir = "/".join(__file__.split("/")[:-1])
    Path(f"{local_dir}/logs.txt").touch(exist_ok=True)
    credential_file = Path(f"{local_dir}/{credentials_path}")
    assert credential_file.exists(), (
        f"No credential file found: '{credential_file}'")
    openai.api_key = str(Path(credential_file).read_text()).strip()
    logging.basicConfig(filename=f"{local_dir}/logs.txt",
                        filemode='a',
                        format=f"{time.asctime()}: %(message)s")
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    language = None
    trans_lan = None
    assert default_translation in translate_prompts.keys(), (
        f"Wrong default translation value: {default_translation}")
    assert isinstance(default_temperature, float) and default_temperature <= 1 and default_temperature >= 0, f"Wrong default temperature value: {default_temperature}"
    assert default_language in cloze_prompts.keys(), f"Wrong default value for language: {default_language}"

    def pl(text, *args, **kwargs):
        "simply print and log"
        text = str(text)
        log.info("PRINTED: " + text)
        print(text, *args, **kwargs)

    # load the previous prompts for autocompletion
    pp_file = Path(f"{local_dir}/previous_prompts.json")
    prev_prompts = []
    try:
        pl("Loading previous prompts from file.")
        assert pp_file.exists(), "Cache file does not exist. Creating it now."
        pp_list = json.load(pp_file.open("r"))
        assert isinstance(pp_list, list), "Invalid cache"
        for i, pp in enumerate(pp_list):
            assert isinstance(pp, dict), "Invalid item in cache"
            assert "prompt" in pp, "Invalid item in cache"
            # pp_list[i] = pp_list[i].replace("\n", "\\n")
        prev_prompts = pp_list
    except Exception as err:
        pl(f"Exception when loading previous prompts : '{err}'")

    pl(f"Loaded {len(prev_prompts)} previous prompts.")

    while True:
        # choose a temperature
        t = ask_user("Temperature settings? (0 to 1)\n>")
        if t == "":
            pl(f"Temperature set to {default_temperature}\n")
            t = default_temperature
        else:
            try:
                t = float(t)
            except Exception:
                pass
        assert isinstance(t, float), f"Wrong value for temperature: {t}"
        assert t <= 1 and t >= 0, (
            "Wrong value for temperature: must be between 0 and 1")

        # choose a mode
        mode = ask_user(f"Mode ? ({', '.join(possible_modes)})\n>",
                        possible_modes)
        if mode == "":
            pl(f"Mode set to {default_mode}\n")
            mode = default_mode
        assert mode in possible_modes

        if mode == "cloze":
            # chose a language
            possible_cloze_languages = cloze_prompts.keys()
            language = ask_user(
                    f"Language? ({', '.join(possible_cloze_languages)})\n>",
                    possible_cloze_languages)
            if language == "":
                pl(f"Language set to {default_language}\n")
                language = default_language
            assert language in possible_cloze_languages, (
                f"Wrong value for language: {language}")
        elif mode == "translate":
            # chose a language
            possible_translation = translate_prompts.keys()
            trans_lan = ask_user(
                f"Language? ({', '.join(possible_translation)})\n>",
                possible_translation)
            if trans_lan == "":
                pl(f"Language set to {default_translation}\n")
                trans_lan = default_translation
            assert trans_lan in possible_translation, (
                f"Wrong value for translation: {trans_lan}")
        elif mode == "paragraph_cloze":
            parser = paragraph_cloze["parser"]
            clozer = paragraph_cloze["clozer"]

        log.info(f"\n\nNew session args: T={t} ; Mode={mode} ; Language={language} ; Translation={trans_lan}")

        pl("\n(Press ctrl+c to go back to settings, again to exit)\n")

        while True:
            try:
                if vi_mode:
                    vimodestr = " (vi mode enabled)"
                else:
                    vimodestr = ""
                user_prompt = ask_user(
                        f"\n\nPrompt:{vimodestr}\n> ",
                        completer_list=[pr["prompt"] for pr in prev_prompts],
                        dont_catch=True,
                        vi_mode=vi_mode,
                        multiline=True).strip()
            except KeyboardInterrupt:
                pl("\n"*3)
                break

            if mode == "cloze":
                if not user_prompt.endswith("?"):
                    # correct space location for question mark
                    if language == "french":
                        user_prompt += " ?"
                    else:
                        user_prompt += "?"
                # makes sure to have a first letter be uppercase
                user_prompt = user_prompt[0].upper() + user_prompt[1:]
                prev_prompts.append({"prompt": user_prompt, "mode": mode})
                p = cloze_prompts[language] + user_prompt + "\nA:"
            elif mode == "translate":
                user_prompt = user_prompt[0].upper() + user_prompt[1:]
                p = translate_prompts[trans_lan] + user_prompt + "'"
            elif mode == "paragraph_cloze":
                prev_prompts.append({"prompt": user_prompt, "mode": mode})
                log.info("Getting struture for prompt :")
                strc_quer = parser + user_prompt + "\nStructure: "
                log.info(f"Qstructure: {strc_quer}")
                try:
                    structure = ask_gpt(strc_quer, t, maximum_tokens)
                    structure = structure["choices"][0]["text"]
                except Exception as err:
                    log.info(f"Exception when parsing structure: '{err}'")
                    pl(f"Exception when parsing structure: '{err}'")
                    continue
                log.info("Astructure: {structure}")
                pl(f"\nStructure parsed:\n{structure}")
                p = clozer + structure + "\nuser_prompt1: "
            elif mode == "freewriting":
                prev_prompts.append(
                        {"prompt": user_prompt.replace("\\n", "\n"),
                         "mode": mode})
                p = user_prompt
            else:
                raise ValueError

            if user_prompt == "":
                pl("Empty user_prompt.")
                continue

            # saving previous prompts
            json.dump(prev_prompts, pp_file.open("w"))

            try:
                response = ask_gpt(p, t, maximum_tokens)
            except KeyboardInterrupt:
                pl("Exit.")
                raise SystemExit()

            pl("\n" + "#" * 20)

            try:
                pl(user_prompt, end=" ")
                ans = str(response["choices"][0]["text"]).strip()
                pl(ans)
                log.info(f"Q: {user_prompt}")
                log.info(f"A: {ans}")
                pl("#" * 20 + "\n")
            except Exception as e:
                pl(f"Error : {str(e)}")


if __name__ == "__main__":
    fire.Fire(run)
