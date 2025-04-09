import subprocess, os, argparse, sys


def confirm_and_move(old, new, yes):
    if yes:
        confirmation = "y"
    else:
        confirmation = input(
            f"rename\n\033[1;32;40m{old}\033[0m\nto\n\033[1;32;40m{new}\033"
            f"[0m?\n(enter/y to confirm, c for custom number, other key to skip): "
        )

    def move_file(old, new):
        # Move the file using subprocess
        subprocess.run(["mv", old, new])
        # Clear the last 5 lines, ensure no artifacts from previous print
        sys.stdout.write("\x1b[1A\x1b[2K" * 5)
        return 1

    if confirmation.lower() in ["y", "\n", "", "yes"]:
        return move_file(old, new)
    elif confirmation.lower() in ["c", "custom"]:
        new_order = input("Enter custom order number: ")
        if new_order.isdigit():
            new_order_str = "[" + str(int(new_order)).zfill(4) + "] "

            # Remove order name from beginning of new filename string ([*]) with regex
            order_idx = new.find("]") + 2
            new = new_order_str + new[order_idx:]

            # Check if the new name already exists
            if os.path.exists(new):
                print(f"File {new} already exists, skipping", old)
                return 0
            
            # Else, repeat the move with the new name
            return confirm_and_move(old, new, yes)
        else:
            print("Invalid order number, skipping", old)
            return 0
    else:
        print("Skipping", old)
        return 0


def rename(path, undo=False, yes=False):
    count = 0

    # cd to the directory
    os.chdir(path)

    for _, _, i in os.walk(path):
        for file in sorted(i):
            if undo:
                if file[0] == "[" and file[5] == "]":
                    file_new = file[7:]
                elif file[0] == " ":
                    file_new = file[1:]
                else:
                    continue
                
                count += confirm_and_move(file, file_new, yes)
            else:
                if file[0] == "[" and file[5] == "]":
                    print("skipping, already renamed", file)
                    continue

                # Custom rules for some magazines
                if file.startswith("Limon 19") and len(file) > 17:
                    no = file[11:14]
                elif file.startswith("Leman [") and len(file) > 17:
                    no = file[18:22]
                elif file.startswith("LEMAN_1991") or file.startswith("LEMAN_2019") \
                        or file.startswith("LEMAN_2020") or file.startswith("LEMAN_2021"):
                    # Get last 4 digits, excluding the extension
                    no = file[-8:-4]
                else:  # Try to detect the first number in the filename
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
                
                # Fix bad chars in filenames
                # (Check alternative encodings for same character with elifs):
                if r"ÅÂ" in new_file:
                    new_file = new_file.replace(r"ÅÂ", "Ş")
                elif r"Å" in new_file:
                    new_file = new_file.replace(r"Å", "Ş")
                
                if r"Ä°" in new_file:
                    new_file = new_file.replace(r"Ä°", "İ")
                if r"Ä±" in new_file:
                    new_file = new_file.replace(r"Ä±", "ı")
                if r"ÅŸ" in new_file:
                    new_file = new_file.replace(r"ÅŸ", "ş")
                if r"Ä" in new_file:
                    new_file = new_file.replace(r"Ä", "Ğ")
                if r"Ä" in new_file:
                    new_file = new_file.replace(r"Ä", "ğ")
                if r"Ã" in new_file:
                    new_file = new_file.replace(r"Ã", "Ü")
                if r"Ã¼" in new_file:
                    new_file = new_file.replace(r"Ã¼", "ü")
                if r"Ã–" in new_file:
                    new_file = new_file.replace(r"Ã", "Ö")
                if r"Ã¶" in new_file:
                    new_file = new_file.replace(r"Ã¶", "ö")
                if r"Ã" in new_file:
                    new_file = new_file.replace(r"Ã", "Ç")
                if r"Ã§" in new_file:
                    new_file = new_file.replace(r"Ã§", "ç")


                count += confirm_and_move(file, new_file, yes)
    
    print("Done, renamed", count, "files")


def detect_missing(path, replace_missing=True):
    print("Detecting missing files...")

    # cd to the directory
    os.chdir(path)
    last_no = 0
    missing = []

    for _, _, i in os.walk(path):
        for file in sorted(i):
            if file[0] == "[" and file[5] == "]":
                no = int(file[1:5])
                if no != last_no + 1:
                    missing.extend(range(last_no + 1, no))
                last_no = no
            else:
                print("skipping unformatted file:", file)
    
    if missing:
        print("Missing files:", missing)
    else:
        print("No missing files until number", last_no)

    if replace_missing:
        for no in missing:
            # Create blank file named "[XXXX] EKSIK"
            filename = f"[{str(no).zfill(4)}] EKSIK"
            with open(filename, "w") as f:
                pass
            print("Created missing magazine file:", filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage a comic book directory from ÇizgiDiyarı")
    parser.add_argument("path", help="Path to the directory")
    parser.add_argument("--undo-rename", help="Undo the renaming", action="store_true")
    parser.add_argument("--yes", help="Skip confirmation", action="store_true")
    parser.add_argument("--no-detect-missing", help="Skip listing missing items", action="store_true")
    parser.add_argument("--no-replace-missing", help="Skip replacing missing itema with blank file", action="store_true")

    args = parser.parse_args()

    path = args.path
    undo = args.undo_rename
    yes = args.yes
    detect_missing_flag = not args.no_detect_missing
    replace_missing_flag = not args.no_replace_missing

    if not os.path.exists(path):
        print("Path does not exist:", path)
        sys.exit(1)

    rename(path, undo, yes)
    if detect_missing_flag:
        detect_missing(path, replace_missing_flag)
