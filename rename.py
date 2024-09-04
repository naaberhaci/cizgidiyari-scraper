import subprocess, os, argparse, sys


def confirm_and_move(old, new, yes):
    if yes:
        confirmation = "y"
    else:
        confirmation = input(f"rename\n\033[1;32;40m{old}\033[0m\nto\n\033[1;32;40m{new}\033[0m? (enter/y to confirm): ")

    if confirmation.lower() in ["y", "\n", "", "yes"]:
        subprocess.run(["mv", old, new])
        # Clear the last 4 lines, ensure no artifacts from previous print
        sys.stdout.write("\x1b[1A\x1b[2K" * 4)
        return 1
    else:
        print("skipping", old)
        return 0


def rename(path, undo=False, yes=False):
    count = 0

    # cd to the directory
    os.chdir(path)

    for _, _, i in os.walk(path):
        for file in i:
            if undo:
                if file[0] == "[" and file[5] == "]":
                    file_new = file[7:]
                elif file[0] == " ":
                    file_new = file[1:]
                else:
                    continue
                
                count += confirm_and_move(file, file_new, yes)
            else:
                if file.startswith("Limon 19") and len(file) > 17:
                    no = file[11:14]
                elif file.startswith("Leman [") and len(file) > 17:
                    no = file[18:22]
                elif file.startswith("LEMAN_1991") or file.startswith("LEMAN_2019") \
                        or file.startswith("LEMAN_2020") or file.startswith("LEMAN_2021"):
                    # Get last 4 digits, excluding the extension
                    no = file[-8:-4]
                else:
                    # Try to detect the first number in the filename
                    no = ""
                    for c in file:
                        if c.isdigit():
                            no += c
                        elif no:
                            break
                    
                    if not no:
                        print("skipping, no number found in", file)
                        continue

                if not no.isdigit():
                    print("skipping, got nondigit no:", no, "from", file)
                    continue

                no = int(no)
                new_file = "[" + str(no).zfill(4) + "] " + file

                # Fix bad filenames
                if "Ä°" in new_file:
                    new_file = new_file.replace("Ä°", "İ")
                if "ÅÂ" in new_file:
                    new_file = new_file.replace("ÅÂ", "Ş")
                
                if "Ä±" in new_file:
                    new_file = new_file.replace("Ä±", "ı")
                if "Ä" in new_file:
                    new_file = new_file.replace("Ä", "ğ")
                if "ÅŸ" in new_file:
                    new_file = new_file.replace("ÅŸ", "ş")
                if "Ã¼" in new_file:
                    new_file = new_file.replace("Ã¼", "ü")
                if "Ã¶" in new_file:
                    new_file = new_file.replace("Ã¶", "ö")
                if "Ã§" in new_file:
                    new_file = new_file.replace("Ã§", "ç")

                
                count += confirm_and_move(file, new_file, yes)
    
    print("Done, renamed", count, "files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename files in a directory")
    parser.add_argument("path", help="Path to the directory - Klasor konumu", nargs="?", required=True)
    parser.add_argument("--undo", help="Undo the renaming - Yeniden isimlendirmeyi geri al", action="store_true")
    parser.add_argument("--yes", help="Skip confirmation - Onaylamalari atla", action="store_true")

    rename(**vars(parser.parse_args()))
