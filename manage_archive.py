import subprocess, os, argparse, sys


LAST_ISSUE_SUFFIX = " - SON SAYI]"


def get_non_digit_idx(file):
    # Find first non-digit character in the filename after the first "["
    idx = 0
    for c in file[1:]:
        idx += 1
        if not c.isdigit():
            break
    
    return idx


def is_formatted(file):
    non_digit_idx = get_non_digit_idx(file)
    
    return file[0] == "[" and \
        (
            file[non_digit_idx] == "]" or \
            file[non_digit_idx:non_digit_idx + len(LAST_ISSUE_SUFFIX)] == LAST_ISSUE_SUFFIX
        )


def confirm_and_move(old, new, yes):
    if yes:
        confirmation = "y"
    else:
        confirmation = input(
            f"Dosya adi\n\033[1;32;40m{old}\033[0m\nyeni isim\n\033[1;32;40m{new}\033"
            f"[0m ile degistirilsin mi?\n(onay icin enter/y, atlamak icin s/n, ya da istediginiz sayiyi giriniz. ESC+enter ile cikabilirsiniz): "
        )

    def clear_lines(n=5):
        # Clear the last n lines, remove artifacts from previous prints
        sys.stdout.write("\x1b[1A\x1b[2K" * n)
        sys.stdout.flush()

    def move_file(old, new):
        # Move the file using subprocess
        subprocess.run(["mv", old, new])
        clear_lines(5)
        return 1

    if confirmation.lower() in ["y", "\n", "", "yes"]:
        return move_file(old, new)
    elif confirmation.isdigit():
        new_order = confirmation
        if new_order.isdigit():
            new_order_str = "[" + str(int(new_order)).zfill(4) + "] "

            # Remove order name from beginning of new filename string ([*]) with regex
            order_idx = new.find("]") + 2
            new = new_order_str + new[order_idx:]

            # Check if the new name already exists
            if os.path.exists(new):
                clear_lines(6)
                print(f"Dosya {new} zaten mevcut, atlaniyor", old)
                return 0
            
            # Else, repeat the move with the new name
            clear_lines(6)
            return confirm_and_move(old, new, yes)
        else:
            clear_lines(6)
            print("Gecersiz sira numarasi, atlaniyor", old)
            return 0
    elif confirmation.lower() in ["s", "skip", "n", "no"]:
        clear_lines(5)
        print("Atlaniyor:", old)
        return 0
    elif confirmation.lower() == "\x1b":  # ESC key
        clear_lines(5)
        print("Cikiliyor...")
        sys.exit(0)
    else:
        clear_lines(5)
        print("Gecersiz girdi, atlaniyor", old)
        return 0


def rename(path, undo=False, yes=False):
    count = 0

    # cd to the directory
    os.chdir(path)

    for _, _, i in os.walk(path):
        for file in sorted(i):
            if undo:
                if is_formatted(file):
                    file_new = file[file.find("]") + 2:]
                elif file[0] == " ":
                    file_new = file[1:]
                else:
                    continue
                
                count += confirm_and_move(file, file_new, yes)
            else:
                if is_formatted(file):
                    print("Atlaniyor, zaten yeniden adlandirilmis:", file)
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
                    temp_no = ""
                    for c in file:
                        if c.isdigit():
                            no += c
                        elif no:
                            if 1900 <= int(no) <= 2030:
                                temp_no = no
                                no = ""
                            else:
                                break

                    if not no:
                        no = temp_no or no

                    if not no:
                        print("Atlaniyor, dosyada numara bulunamadi:", file)
                        continue

                if not no.isdigit():
                    print(f"Atlaniyor, gecersiz sayi numarasi {no} elde edildi:", file)
                    continue

                no = int(no)
                new_file = "[" + str(no).zfill(4) + "] " + file
                
                # Fix bad chars in filenames
                # (Check alternative encodings for same character with elifs):
                if r"ÅÂ" in new_file:
                    new_file = new_file.replace(r"ÅÂ", "Ş")
                elif r"Å" in new_file:
                    new_file = new_file.replace(r"Å", "Ş")
                elif r"Å" in new_file:
                    new_file = new_file.replace(r"Å", " Ş")
                elif r"sÌ§" in new_file:
                    new_file = new_file.replace(r"sÌ§", "ş")
                
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
            if is_formatted(file):
                no = int(file[1:get_non_digit_idx(file)])
                if no != last_no + 1:
                    missing.extend(range(last_no + 1, no))
                last_no = no
            else:
                print("Atlaniyor, formatlanmamis dosya:", file)
    
    if missing:
        print("Eksik dosyalar:", missing)
    else:
        print(f"{last_no} numarasina kadar eksik dosya bulunamadi")

    if replace_missing:
        for no in missing:
            # Create blank file named "[XXXX] EKSIK"
            filename = f"[{str(no).zfill(4)}] EKSIK"
            with open(filename, "w") as f:
                pass
            print("Eksik sayi icin dosya olusturuldu:", filename)

        # Cleanup placeholders: remove empty "[XXXX] EKSIK" files if an actual file with the same index exists.
        for fname in sorted(os.listdir(path)):
            if not fname.startswith("[") or not fname.endswith("EKSIK"):
                continue

            fullpath = os.path.join(path, fname)
            if not os.path.isfile(fullpath):
                continue

            try:
                # only consider empty placeholder files
                if os.path.getsize(fullpath) != 0:
                    continue
            except OSError:
                continue

            # extract the number between [ and ]
            end_idx = fname.find("]")
            if end_idx == -1:
                continue
            num = fname[1:end_idx]

            # look for any other non-empty file that starts with the same [num]
            for other in sorted(os.listdir(path)):
                if other == fname:
                    continue
                if not other.startswith(f"[{num}]"):
                    continue

                other_full = os.path.join(path, other)
                if not os.path.isfile(other_full):
                    continue

                try:
                    if os.path.getsize(other_full) > 0:
                        try:
                            os.remove(fullpath)
                            print("Gecici dosya silindi:", fname)
                        except OSError:
                            print("Gecici dosya silinirken hata olustu:", fname)
                        break
                except OSError:
                    continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ÇizgiDiyarı'ndan alınan arşivleri yeniden adlandırmak ve eksik dosyaları tespit etmek için bir araç.")
    parser.add_argument("path", help="Arsiv dosyalarının bulunduğu dizin yolu")
    parser.add_argument("--undo-rename", help="Yeniden adlandırmayı geri al", action="store_true")
    parser.add_argument("--yes", help="Onaylamayı atla", action="store_true")
    parser.add_argument("--no-detect-missing", help="Eksik öğeleri listelemeyi atla", action="store_true")
    parser.add_argument("--no-replace-missing", help="Eksik öğeleri boş dosyalarla değiştirme", action="store_true")

    args = parser.parse_args()

    path = args.path
    undo = args.undo_rename
    yes = args.yes
    detect_missing_flag = not args.no_detect_missing
    replace_missing_flag = not args.no_replace_missing

    if not os.path.exists(path):
        print("Dizin mevcut degil:", path)
        sys.exit(1)

    rename(path, undo, yes)
    if detect_missing_flag:
        detect_missing(path, replace_missing_flag)
