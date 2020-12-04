# Instagram unfollower tracker
Tracks who has unfollowed you on instagram since you last ran the script.

Usage:
1. Replace text with login credentials in text file login.txt
2. Ensure selenium and webdriver_manager packages are installed
  -- You can install them with the following commands
    -- pip install selenium
    -- pip install webdriver_manager
3. Replace line 61 with your profile link.
  -- It's important to keep the '/followers/' at the end of the URL
4. Run the script
5. All followers are saved in the text file followers.txt
6. If anyone has unfollowed you since you last ran the script, they will show up in the text file unfollowers.txt
