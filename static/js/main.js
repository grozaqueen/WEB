function getCookie(name) {
  const cookies = document.cookie.split(';').map(cookie => cookie.trim());
  const targetCookie = cookies.find(cookie => cookie.startsWith(`${name}=`));
  return targetCookie ? decodeURIComponent(targetCookie.substring(name.length + 1)) : null;
}

const likesQuestionsList = document.getElementsByClassName('like-questions-list');
const likesAnswerList = document.getElementsByClassName('like-answer-list');

for (let item of likesQuestionsList) {
    const DislikeBtn = item.children[0].children[0].children[0];
    const Counter = item.children[0].children[0].children[1];
    const LikeBtn = item.children[0].children[0].children[2];

    DislikeBtn.addEventListener('click', () => {
        const bodyReq = new FormData();
        bodyReq.append('item_id', item.dataset.id);
        bodyReq.append('rate_type', 'dislike');
        bodyReq.append('item_type', 'question');
        const request = new Request('/rate/', {
            method: 'POST',
            body: bodyReq,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                Counter.innerHTML = data.count;
                if (data.count < 0)
                    Counter.style.color = "red";
                else
                    Counter.style.color = "green";
            })
    });

    LikeBtn.addEventListener('click', () => {
        const bodyReq = new FormData();
        bodyReq.append('item_id', item.dataset.id);
        bodyReq.append('rate_type', 'like');
        bodyReq.append('item_type', 'question');
        const request = new Request('/rate/', {
            method: 'POST',
            body: bodyReq,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                Counter.innerHTML = data.count;
                if (data.count >= 0)
                    Counter.style.color = "green";
                else
                    Counter.style.color = "red";

            })
    });
}

for (let item of likesAnswerList) {
  const answerId = item.dataset.id;
  const likeBtn = item.querySelector('.like-btn');
  const dislikeBtn = item.querySelector('.dislike-btn');
  const counter = item.querySelector('#rating-count-' + answerId);

  likeBtn.addEventListener('click', () => {
    const bodyReq = new FormData();
    bodyReq.append('item_id', answerId);
    bodyReq.append('rate_type', 'like');
    bodyReq.append('item_type', 'answer');
    const request = new Request('/rate/', {
      method: 'POST',
      body: bodyReq,
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
      }
    })
    fetch(request)
      .then((response) => response.json())
      .then((data) => {
        counter.innerHTML = data.count;
        if (data.count >= 0)
          counter.style.color = "green";
        else
          counter.style.color = "red";
      })
  });

  dislikeBtn.addEventListener('click', () => {
    const bodyReq = new FormData();
    bodyReq.append('item_id', answerId);
    bodyReq.append('rate_type', 'dislike');
    bodyReq.append('item_type', 'answer');
    const request = new Request('/rate/', {
      method: 'POST',
      body: bodyReq,
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
      }
    })
    fetch(request)
      .then((response) => response.json())
      .then((data) => {
        counter.innerHTML = data.count;
        if (data.count < 0)
          counter.style.color = "red";
        else
          counter.style.color = "green";
      })
  });
}


const checkboxes = document.querySelectorAll('input[type="checkbox"]');

checkboxes.forEach((checkbox) => {
    checkbox.addEventListener('click', (e) => {

        const answerId = checkbox.parentNode.dataset.id;
        const bodyReq = new FormData();
        bodyReq.append('answer_id', answerId);
        bodyReq.append('is_correct', checkbox.checked);

        fetch('/correct/', {
            method: 'POST',
            body: bodyReq,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })

        .then((response) => response.json())
        .then((data) => {

            console.log(data);
        })
        .catch((error) => {

            console.error(error);
        });
    });
});

