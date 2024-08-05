document.addEventListener('DOMContentLoaded', (event) => {
    fetch('/${site_id}/languages') 
        .then(response => response.json())
        .then(languages => {
            const populateSelect = (selectId) => {
                const selectElement = document.getElementById(selectId);
                languages.forEach(language => {
                    const option = document.createElement('option');
                    option.value = language.code;
                    option.textContent = language.name;
                    selectElement.appendChild(option);
                });
            };

            populateSelect('languageInputSelect');
            populateSelect('languageTranslationSelect');

            const userLang = navigator.language || navigator.userLanguage;
            const setDefaultLanguage = (selectId) => {
                const selectElement = document.getElementById(selectId);
                for (let i = 0; i < selectElement.options.length; i++) {
                    if (selectElement.options[i].value === userLang.substring(0, 2)) {
                        selectElement.selectedIndex = i;
                        break;
                    }
                }
            };

            setDefaultLanguage('languageInputSelect');
            setDefaultLanguage('languageTranslationSelect');
        })
        .catch(error => console.error('Error fetching languages:', error));
});