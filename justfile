default: commit push

commit:
    git add .
    cz commit

push:
    git push

bump:
    cz bump
    git push
    git push --tags

format:
    isort .
    black .
    alejandra .