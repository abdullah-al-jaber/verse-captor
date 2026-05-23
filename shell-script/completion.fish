# verse-captor completions

complete -c verse-captor -l start-url -r -d "Start URL for scraping novel chapter"
complete -c verse-captor -l stop-url -r -d "Stop URL for scraping novel chapter"
complete -c verse-captor -l file-path -r -d "File Path for novel chapter urls"
complete -c verse-captor -l folder-path -r -d "Folder Path for novel chapter texts"
complete -c verse-captor -l text-selector -r -d "Selector for extracting text from HTML"
complete -c verse-captor -l url-selector -r -d "Selector for extracting URL from HTML"

complete -c verse-captor -l help -d "Show help and exit"
