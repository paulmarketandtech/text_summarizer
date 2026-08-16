## TEXT SUMMARIZER

### Idea behind the project

tl;dr: app summarizes Youtube stock related videos.

#### Bit more details 
User provides a Youtube url which is stock market related.
Then the app downloads the transcript via yt_dlp [github repo](https://github.com/yt-dlp/yt-dlp/).
Summarizes it and display to the user.

The app was design to work with YT but i tried to do it as generic as possible because in the future i'm planning to expand it to different sources.
And i believe if you do some small tweaks in the code and add some proper prompting then it will handle all kind of videos.
I'm running it locally on RTX3060 6GB VRAM but luckily QWEN2.5:7b handles well summarizing (not too big) chunks of data.


NOTE. This app is not perfect and by design will never be, if only because of a problem I can't get around: yt_dlp.
It's a great library, don't get me wrong, but it downloads ai-generated transcript (youtube makes them on the fly) and often they have issues which (probably) can't be solved.
Sometimes when the creator talks too fast, uses uncommon words/naming then google's ai don't understand it and make up stuff.
Example: I was working on a podcast which was 100% about Applovin stock, ticker $APP. There was not a single mention about Apple $AAPL, but in the transcript 
sometimes there was Applovin but sometimes there was "Apple 11".

Bottom line: If you're looking for an app which will give you all the answers, what to buy and sell then this is not for you.
If you're looking for an app which quickly tell you what people are talking about and what's the sentiment on the market and you're able to do some searching by yourself then i hope you'll enjoy this app.
<img width="1326" height="891" alt="image" src="https://github.com/user-attachments/assets/d7d20e8a-4f22-4936-9f6d-e4e95e790c7e" />
