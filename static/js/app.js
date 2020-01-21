document.addEventListener("DOMContentLoaded", function() {
  /**
   * HomePage - Help section
   */
  class Help {
    constructor($el) {
      this.$el = $el;
      this.$buttonsContainer = $el.querySelector(".help--buttons");
      this.$slidesContainers = $el.querySelectorAll(".help--slides");
      this.currentSlide = this.$buttonsContainer.querySelector(".active").parentElement.dataset.id;
      this.init();
    }

    init() {
      this.events();
    }

    events() {
      /**
       * Slide buttons
       */
      this.$buttonsContainer.addEventListener("click", e => {
        if (e.target.classList.contains("btn")) {
          this.changeSlide(e);
        }
      });

      /**
       * Pagination buttons
       */
      this.$el.addEventListener("click", e => {
        if (e.target.classList.contains("btn") && e.target.parentElement.parentElement.classList.contains("help--slides-pagination")) {
          this.changePage(e);
        }
      });
    }

    changeSlide(e) {
      e.preventDefault();
      const $btn = e.target;

      // Buttons Active class change
      [...this.$buttonsContainer.children].forEach(btn => btn.firstElementChild.classList.remove("active"));
      $btn.classList.add("active");

      // Current slide
      this.currentSlide = $btn.parentElement.dataset.id;

      // Slides active class change
      this.$slidesContainers.forEach(el => {
        el.classList.remove("active");

        if (el.dataset.id === this.currentSlide) {
          el.classList.add("active");
        }
      });
    }

    /**
     * TODO: callback to page change event
     */
    changePage(e) {
      e.preventDefault();
      const page = e.target.dataset.page;

      console.log(page);
    }
  }
  const helpSection = document.querySelector(".help");
  if (helpSection !== null) {
    new Help(helpSection);
  }

  /**
   * Form Select
   */
  class FormSelect {
    constructor($el) {
      this.$el = $el;
      this.options = [...$el.children];
      this.init();
    }

    init() {
      this.createElements();
      this.addEvents();
      this.$el.parentElement.removeChild(this.$el);
    }

    createElements() {
      // Input for value
      this.valueInput = document.createElement("input");
      this.valueInput.type = "text";
      this.valueInput.name = this.$el.name;

      // Dropdown container
      this.dropdown = document.createElement("div");
      this.dropdown.classList.add("dropdown");

      // List container
      this.ul = document.createElement("ul");

      // All list options
      this.options.forEach((el, i) => {
        const li = document.createElement("li");
        li.dataset.value = el.value;
        li.innerText = el.innerText;

        if (i === 0) {
          // First clickable option
          this.current = document.createElement("div");
          this.current.innerText = el.innerText;
          this.dropdown.appendChild(this.current);
          this.valueInput.value = el.value;
          li.classList.add("selected");
        }

        this.ul.appendChild(li);
      });

      this.dropdown.appendChild(this.ul);
      this.dropdown.appendChild(this.valueInput);
      this.$el.parentElement.appendChild(this.dropdown);
    }

    addEvents() {
      this.dropdown.addEventListener("click", e => {
        const target = e.target;
        this.dropdown.classList.toggle("selecting");

        // Save new value only when clicked on li
        if (target.tagName === "LI") {
          this.valueInput.value = target.dataset.value;
          this.current.innerText = target.innerText;
        }
      });
    }
  }
  document.querySelectorAll(".form-group--dropdown select").forEach(el => {
    new FormSelect(el);
  });

  /**
   * Hide elements when clicked on document
   */
  document.addEventListener("click", function(e) {
    const target = e.target;
    const tagName = target.tagName;

    if (target.classList.contains("dropdown")) return false;

    if (tagName === "LI" && target.parentElement.parentElement.classList.contains("dropdown")) {
      return false;
    }

    if (tagName === "DIV" && target.parentElement.classList.contains("dropdown")) {
      return false;
    }

    document.querySelectorAll(".form-group--dropdown .dropdown").forEach(el => {
      el.classList.remove("selecting");
    });
  });

  /**
   * Switching between form steps
   */
  class FormSteps {
    constructor(form) {
      this.$form = form;
      this.$next = form.querySelectorAll(".next-step");
      this.$prev = form.querySelectorAll(".prev-step");
      this.$step = form.querySelector(".form--steps-counter span");
      this.currentStep = 1;

      this.$stepInstructions = form.querySelectorAll(".form--steps-instructions p");
      const $stepForms = form.querySelectorAll("form > div");
      this.slides = [...this.$stepInstructions, ...$stepForms];

      this.init();
    }

    /**
     * Init all methods
     */
    init() {
      this.events();
      this.updateForm();
    }

    /**
     * All events that are happening in form
     */
    events() {
      // Next step
      this.$next.forEach(btn => {
        btn.addEventListener("click", e => {
          e.preventDefault();
          this.currentStep++;
          this.updateForm();
        });
      });

      // Previous step
      this.$prev.forEach(btn => {
        btn.addEventListener("click", e => {
          e.preventDefault();
          this.currentStep--;
          this.updateForm();
        });
      });

      // Form submit
      this.$form.querySelector("form").addEventListener("submit", e => this.submit(e));
    }

    /**
     * Update form front-end
     * Show next or previous section etc.
     */
    updateForm() {
      this.$step.innerText = this.currentStep;

      if (this.currentStep == 1) {
        $("input[name='institution']").each(function () {
          $(this).closest('div').hide();
        })
      }

      // Ajax -  get matching institutions
      if (this.currentStep == 2) {
        let senderData = JSON.stringify({'category_list': categoryList});
        let csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
        $.ajax({
          headers: {"X-CSRFToken": csrftoken},
          type: 'POST',
          url: '/ajax/organizations/id/',
          data: senderData,
          dataType: 'text',
          success: function (data) {
            let response = JSON.parse(data);
            let organizations_id_dict_list = response['organizations_id'];
            $("input[name='institution']").each(function() {
              for (let item in organizations_id_dict_list) {
                if ($(this).val() == organizations_id_dict_list[item]['id']) {
                  $(this).closest('div').show();
                  break;
                }
                else {
                    $(this).closest('div').hide();
                }
              }
            })
          }
        });
      }

      if (this.currentStep == 5) {
        let input_address = $("input[name='address']").val();
        let input_city = $("input[name='city']").val();
        let input_zip_code = $("input[name='zip_code']").val();
        let input_phone_number = $("input[name='phone_number']").val();
        let input_pick_up_date = $("input[name='pick_up_date']").val();
        let input_pick_up_time = $("input[name='pick_up_time']").val();
        let input_pick_up_comment = $("textarea[name='pick_up_comment']").text();

        let address_ok = false;
        let city_ok = false;
        let zip_code_ok = false;
        let phone_number_ok = false;
        let pick_up_date_ok = false;
        let pick_up_time_ok = false;

        $('.address--summary').text(input_address);
        $('.city--summary').text(input_city);
        $('.postcode--summary').text(input_zip_code);
        $('.phone--summary').text(input_phone_number);
        $('.date--summary').text(input_pick_up_date);
        $('.time--summary').text(input_pick_up_time);

        if (input_address.length > 0) {
          address_ok = true;
        }

        if (input_city.length > 0) {
          city_ok = true;
        }

        if (input_zip_code.length == 6) {
          zip_code_ok = true;
        }

        if (input_phone_number.length > 0) {
          phone_number_ok = true;
        }

        if (input_pick_up_date.length == 10) {
          pick_up_date_ok = true;
        }

        if (input_pick_up_time.length != 0) {
          pick_up_time_ok = true;
        }

        if (input_pick_up_comment.length != 0) {
          $('.more_info--summary').text(input_pick_up_comment);
        }
        else {
          $("textarea[name='pick_up_comment']").text('Brak uwag');
          $('.more_info--summary').text('Brak uwag');
        }

        if (address_ok && city_ok && zip_code_ok && phone_number_ok && pick_up_date_ok && pick_up_time_ok) {
          $('.btn-next-step5').text('Potwierdzam');
          $('.btn-next-step5').prop('disabled', false);
        }
        else {
          $('.btn-next-step5').text('Wypełnij poprawnie pola adresu i kontaktu z kroku 4!');
          $('.btn-next-step5').prop('disabled', true);
        }

      }

      // TODO: Validation

      this.slides.forEach(slide => {
        slide.classList.remove("active");

        if (slide.dataset.step == this.currentStep) {
          slide.classList.add("active");
        }
      });

      this.$stepInstructions[0].parentElement.parentElement.hidden = this.currentStep >= 6;
      this.$step.parentElement.hidden = this.currentStep >= 6;

      // TODO: get data from inputs and show them in summary
    }

    /**
     * Submit form
     *
     * TODO: validation, send data to server
     */
    submit(e) {
      // e.preventDefault();
      this.currentStep++;
      this.updateForm();
    }
  }
  const form = document.querySelector(".form--steps");
  if (form !== null) {
    new FormSteps(form);
  }

  // Step 1 -  List of selected categories and next button enabling/disabling
  var categoryList = [];
  $("input[name='categories']").click(function() {
    if($(this).is(":checked")){
      categoryList.push($(this).val());
      $('.btn-next-step1').prop('disabled', false);
      }
    else if($(this).is(":not(:checked)")){
          for (let i=0; i < categoryList.length; i++) {
            if (categoryList[i] == $(this).val())
            categoryList.splice(i, 1);
          }
          $('.btn-next-step1').prop('disabled', true);
      }
    });

  // Step 2 - validation
  $("input[name='quantity']").keyup(function () {
    if ($(this).val() > 0 ) {
      $('.btn-next-step2').prop('disabled', false);
      let bags = 'Worki 60L: ' + $(this).val();
      $('.summary--text.bags').text(bags);
    }
    else {
      $('.btn-next-step2').prop('disabled', true);
    }
  });

  // Step 3 - validation
  $("input[name='institution']").click(function () {
    if ($(this).is(":checked")) {
      $('.btn-next-step3').prop('disabled', false);
      let chosen_institution_name = $(this).siblings('.description').children('div .title').text();
      $('.summary--text.institution').text('Dla: "' + chosen_institution_name + '"');
    }
  });
  });
