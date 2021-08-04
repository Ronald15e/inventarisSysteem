function myFunction() {
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    ul = document.getElementById("myUL");
    li = ul.getElementsByTagName("article");
    for (i = 0; i < li.length; i++) {
        h1 = li[i].getElementsByTagName("h1")[0];
        a1 = li[i].getElementsByTagName("a")[0];
        a2 = li[i].getElementsByTagName("a")[1];
        a3 = li[i].getElementsByTagName("a")[2];
        a4 = li[i].getElementsByTagName("a")[3];

        contentHeader = h1.textContent || h1.innerText;
        value1 = a1.textContent || a1.innerText;
        value2 = a2.textContent || a2.innerText;
        value3 = a3.textContent || a3.innerText;
        value4 = a4.textContent || a4.innerText;

        if (value1.toUpperCase().indexOf(filter) > -1 || value2.toUpperCase().indexOf(filter) > -1 || value3.toUpperCase().indexOf(filter) > -1 || value4.toUpperCase().indexOf(filter) > -1 || contentHeader.toUpperCase().indexOf(filter) > -1 ) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}