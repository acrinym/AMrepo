# Rewatching Death Stranding Cutscenes

#### You:
Can I go back through the death stranding videos once I beat the game? I thought I could rewatch briefings and stuff

#### ChatGPT:


#### ChatGPT:
iturn0image1turn0image2turn0image3turn0image6In *Death Stranding*, once you've completed the game, your ability to revisit cutscenes and briefings is somewhat limited. Here's how you can revisit certain content:

### 🎬 Rewatching Cutscenes and Briefings

- **BB Flashbacks**: You can rewatch BB's flashback scenes by interacting with the green figurines in Sam's Private Room. These are accessible post-game and allow you to revisit specific memories. citeturn0search2

- **Nightmare Sequences**: Some players have reported that certain cutscenes, particularly those related to BB, can be re-experienced through the nightmare scenarios that occur when Sam rests in his Private Room. citeturn0search1

### ❌ Limitations

- **Main Story Cutscenes**: Unfortunately, there isn't a built-in feature to rewatch all main story cutscenes or briefings directly from the game's menu. To revisit these, you'd need to load a previous save file from before completing the game. citeturn0search1

- **Mission Replays**: The game doesn't offer a chapter select or mission replay feature. To replay specific missions or experience certain cutscenes again, you'd need to have manual save files from those points in the game. Otherwise, starting a new game would be necessary.

### 📺 Alternative Options

- **Online Videos**: If you're looking to re-experience the story without replaying the game, there are comprehensive compilations of all cutscenes available online. For instance, this [YouTube video](https://www.youtube.com/watch?v=HfrCcKDzOow) offers a full movie-style presentation of *Death Stranding: Director's Cut* cutscenes.

If you need assistance locating specific scenes or briefings, feel free to ask!


#### You:
I have dsdc and I want to back it up before I start a new game cuz I don't want to lose my current progress which is post game, where do I go to do that. I have it on epic games

#### ChatGPT:
iturn0image0turn0image2turn0image4turn0image9To back up your **Death Stranding Director’s Cut** save on **Epic Games** before starting a new game, follow these steps:

---

### 📁 Locate Your Save Files

Your save files are stored in the following directory:

```

C:\Users$YourUsername]\AppData\LocalLow\KojimaProductions\DeathStrandingDC\
```



**Note**: The `AppData` folder is hidden by default. To access it:

- Open File Explorer.
- Click on the **View** tab.
- Check the box for **Hidden items**.

---

### 💾 Back Up Your Save Files

1. Navigate to the directory mentioned above.
2. Copy the entire `DeathStrandingDC` folder.
3. Paste it to a secure location, such as an external drive or a cloud storage service.

This backup ensures you can restore your post-game progress if needed.

---

### 🔄 Restoring Your Save Files

If you wish to restore your backed-up save:

1. Ensure the game is **not running**.
2. Navigate to the original save directory:

   ```
   C:\Users$YourUsername]\AppData\LocalLow\KojimaProductions\DeathStrandingDC\
   ```



3. Replace the contents of this folder with your backed-up files.
4. Launch the game.

Your post-game progress should now be restored.

---

### 📺 Additional Resource

For a visual guide on locating and backing up your save files, you might find this video helpful:

videoWhere Is The Save Game Files Located On PCturn0search2

Feel free to reach out if you need further assistance!


#### You:
Oh, cusers huh. I think not lol

#### ChatGPT:
Haha fair—**Windows loves stuffing everything in `C:\Users` like it’s a digital junk drawer.** But yep, that’s where your **Death Stranding: Director’s Cut** save files hide out, even if it *feels wrong*.

Here’s the rogue’s map again, for the brave:

```
C:\Users\<YourUsername>\AppData\LocalLow\KojimaProductions\DeathStrandingDC\
```

If you’re thinking *“nah, let me redirect this whole operation,”* you could:

### Optional: Symbolic Link Magic

If you want to trick the game into saving somewhere *more reasonable*, like a D:\GameSaves drive:

1. **Backup original folder** first.
2. Delete the original `DeathStrandingDC` folder.
3. Open CMD as Administrator.
4. Run:
   ```
   mklink /D "C:\Users\<YourUsername>\AppData\LocalLow\KojimaProductions\DeathStrandingDC" "D:\GameSaves\DeathStrandingDC"
   ```

Now your saves are in D:\ like a civilized setup, but the game thinks it’s business as usual.

Let me know if you want an automated script or extra backup strategies (like syncing to cloud on exit). I got you.
