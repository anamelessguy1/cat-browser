const removeRadius = el => el.style.borderRadius = "0px";

document.querySelectorAll("*").forEach(removeRadius);

const observer = new MutationObserver(mutations => {
    mutations.forEach(m => {
        m.addedNodes.forEach(node => {
            if (node.nodeType === 1) removeRadius(node);
            if (node.querySelectorAll) node.querySelectorAll("*").forEach(removeRadius);
        });
    });
});

observer.observe(document.body, { childList: true, subtree: true });
