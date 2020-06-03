import '../scss/preplan.scss';

var gender, age, height, weight, bodyFat, pal, palMap, kBmr ,tmp;

function addEventListeners() {
  // Fetch client data on select change
  $('#id_client').change(function() {
    if ($(this).val()) {
      $('#spinner').show();
      fetch('/main/client/' + $('#id_client').val() + '/data/')
        .then(response => {
          if (response.status === 404) {
            alert('O cliente não foi encontrado.');
            throw 'Client not found.';
          }
          return response.json();
        })
        .then(data => {
          updateClientData(data)
          render();
          $('#wrapper').css('opacity', 1).removeClass('disabled');
          $('#spinner').hide();
        });
    }
    else {
      $('#wrapper').addClass('disabled').css('opacity', 0.5);
    }
  }).change();

  $('.efield .field-value').click(function edit() {
    tmp = $(this).parent().hide()
        .siblings('.efield-controls').css('display', 'flex')
          .children('input, select').focus().val();
  });

  $('.efield input').focus(function(event) {
    event.target.select();
  });

  function save(self, value) {
    $(self).parents('.efield-controls').hide()
      .siblings('.field').show();
    render();
  }

  function cancel(self) {
    $(self).val(tmp).parent().hide()
      .siblings('.field').show();
  }

  $('.efield-save').click(function(event) {
    event.preventDefault();
    save(this, $(this).parent().siblings('input').val());
  });

  $('.efield input[type!="range"], .efield select').blur(function() {
    if (!event.relatedTarget || !event.relatedTarget.classList.contains('efield-save')) {
      cancel(this);
    }
  }).keydown(function(event) {
    if (event.key === 'Enter' || event.key === 'Tab') save(this, $(this).val());
    else if (event.key === 'Escape') cancel(this);
  });

  // Set range input label values
  $('.efield input[type="range"]').on('input', function() {
    $(this).parent().siblings('.field-extra').text($(this).val());
  }).trigger('input');

  $('.efield input[type="range"]').change(render);

  // Range inputs interdependence
  const mns = ['protein', 'carbs', 'fats', 'protein', 'carbs'].map(mn => $(`#${mn}_efield input`));
  for (let i = 0; i < 3; i++) {
    mns[i].on('input', function() {
      const secondVal = Math.max(100 - $(this).val() - mns[i+2].val(), 0);
      mns[i+1].val(secondVal).parent().siblings('.field-extra').text(secondVal);
      if (secondVal === 0) {
        const thirdVal = 100 - $(this).val();
        mns[i+2].val(thirdVal).parent().siblings('.field-extra').text(thirdVal);
      }
    });
  }
}
addEventListeners();

function updateClientData(data) {
  gender = data.gender;
  age = data.age;
  height = data.height;
  weight = data.weight;
  bodyFat = data.bodyFat;
  console.log(bodyFat);
  pal = data.pal;
  palMap = data.palMap;
  kBmr = 6.25*height - 5*age + { m: 5, f: -161 }[gender];
  $('#weight').text(weight);
  $('#body_fat').text(bodyFat);
  $('#pal').text(palMap[pal]);
  $('#pal_extra').text('PAL ' + pal);
  $('#bmi').text(properRound(weight / (height / 100) ** 2, 1));
  const bmr = 10 * weight + kBmr;
  $('#bmr').text(Math.round(bmr));
  $('#daily_energy').text(Math.round(bmr * pal));
}

function properRound(value, places) {
  const multiplier = 10 ** places;
  return Math.round(value * multiplier) / multiplier;
}

function render() {  //TODO? try without parseFloat
  const goalWeight = parseFloat($('#goal_weight_efield input').val());
  const goalBodyFat = parseFloat($('#goal_body_fat_efield input').val());
  const newPal = $('#new_pal_efield select').val();
  
  const goalTime = parseFloat($('#goal_time_efield input').val());
  const palChange = parseFloat($('#pal_change_efield input').val());
  const goalDailyEnergy = parseFloat($('#goal_daily_energy_efield input').val());

  const regularMilk = parseInt($('#regular_milk_efield input').val());
  const lowFatMilk = parseInt($('#low_fat_milk_efield input').val());
  const solidYoghurt = parseInt($('#solid_yoghurt_efield input').val());
  const liquidYoghurt = parseInt($('#liquid_yoghurt_efield input').val());
  const whey = parseInt($('#whey_efield input').val());
  const fruit = parseInt($('#fruit_efield input').val());
  const vegetables = parseInt($('#vegetables_efield input').val());

  const protein = parseFloat($('#protein_efield input').val()) / 100;
  const carbs = parseFloat($('#carbs_efield input').val()) / 100;
  const fats = parseFloat($('#fats_efield input').val()) / 100;

  const proteinWeight = Math.round(goalDailyEnergy * protein / 4);
  const carbsWeight = Math.round(goalDailyEnergy * carbs / 4);
  const fatsWeight = Math.round(goalDailyEnergy * fats / 9);

  // Update efield fields text  //TODO? run this on init and save
  $('#goal_weight').text(goalWeight);  //TODO? general assigment for all elements
  $('#goal_body_fat').text(goalBodyFat);
  $('#new_pal').text(palMap[newPal]);

  $('#goal_time').text(goalTime);
  $('#pal_change').text(palChange);

  $('#goal_daily_energy').text(goalDailyEnergy);

  $('#regular_milk').text(regularMilk);
  $('#low_fat_milk').text(lowFatMilk);
  $('#solid_yoghurt').text(solidYoghurt);
  $('#liquid_yoghurt').text(liquidYoghurt);
  $('#whey').text(whey);
  $('#fruit').text(fruit);
  $('#vegetables').text(vegetables);
  
  // Update computed fields
  $('#goal_weight_extra').text(getSignal(properRound(goalWeight - weight, 1)) + ' kg');
  $('#goal_body_fat_extra').text(getSignal(properRound(goalBodyFat - bodyFat), 1) + ' %');
  $('#new_pal_extra').text('PAL ' + newPal);
  
  setTimeout(() => niddk({
      gender: { m: 'Male', f: 'Female' }[gender],
      age,
      height,
      weight,
      pal: parseFloat(pal),
      goalWeight: goalWeight,
      goalTime: goalTime * 30,
      palChange,
    })
  );
  
  $('#goal_bmi').text(properRound(goalWeight / (height / 100) ** 2, 1));
  const goalBmr = 10 * goalWeight + kBmr;
  $('#goal_bmr').text(Math.round(goalBmr));
  $('#goal_daily_energy_extra').text(Math.round(goalBmr * newPal) + ' kcal/dia');

  $('#protein_weight').text(proteinWeight);
  $('#carbs_weight').text(carbsWeight);
  $('#fats_weight').text(fatsWeight);

  $('#protein_per_weight').text(properRound(proteinWeight / weight, 2));
  $('#carbs_per_weight').text(properRound(carbsWeight / weight, 2));
  $('#fats_per_weight').text(properRound(fatsWeight / weight, 2));

  setTimeout(() => findDosages({
    totalProtein: proteinWeight,
    totalCarbs: carbsWeight,
    totalFats: fatsWeight,
    totalCalories: goalDailyEnergy,
  }, { regularMilk, lowFatMilk, solidYoghurt, liquidYoghurt, whey, fruit, vegetables }));
}

function getSignal(value) {
  return (value >= 0 ? '+ ' : '- ') + Math.abs(value);
}

function niddk(data) {
  const calc = document.getElementById('calc');
  $('#energy_to_goal, #energy_to_maintain').text('...');
  while (calc.contentDocument.readyState !== 'complete') {
    setTimeout(() => niddk(data), 500);
    return;
  }
  for (let key in data) {
    if (typeof data[key] === 'undefined' || (typeof data[key] === 'number' && Number.isNaN(data[key]))) {
      return;
    }
  }
  const calcBody = calc.contentDocument.body;
  const scope = calc.contentWindow.angular.element(calcBody).scope();
  const result = scope.getEnergy(data);
  $('#energy_to_goal').text(result.energyGoal);
  $('#energy_to_maintain').text(result.energyMaintain);
}

function findDosages(totals, initialDosages) {
  for (let arg of [totals, initialDosages]) {
    for (let key in arg) {
      if (typeof arg[key] === 'undefined' || (typeof arg[key] === 'number' && Number.isNaN(arg[key]))) {
        return;
      }
    }
  }
  
  let { totalProtein, totalCarbs, totalFats, totalCalories } = totals;
  const {
    regularMilk, lowFatMilk, solidYoghurt, liquidYoghurt, whey, fruit, vegetables
  } = initialDosages;
  const initialDosagesArray = [
    regularMilk, lowFatMilk, solidYoghurt, liquidYoghurt, whey, fruit, vegetables
  ];

  totalProtein -= dot(initialDosagesArray, [7, 7, 16.5, 12.1, 19.5, 0, 2]);
  totalCarbs -= dot(initialDosagesArray, [12, 10, 6, 8.2, 1, 10, 5]);
  totalFats -= dot(initialDosagesArray, [4, 1.2, 0.3, 0.7, 1.8, 0, 0]);
  totalCalories -= dot(initialDosagesArray, [106, 80, 93, 87, 98, 50, 25]);
  const totalsArray = [totalProtein, totalCarbs, totalFats, totalCalories];

  const maxProtein = Math.ceil(Math.min(totalProtein / 7, totalFats / 3));
  const maxCarbs = Math.ceil(Math.min(totalProtein / 2, totalCarbs / 15));
  const maxFats = Math.ceil(totalFats / 5);

  const factorVectors = [
    [7, 2, 0],
    [0, 15, 0],
    [3, 0, 5],
    [55, 70, 45],
  ];
  
  let dosages, optimalDosages = null;
  let minError = 1000;

  for (let protein = 7, error = 0; protein <= maxProtein; protein++) {
    for (let carbs = 7; carbs <= maxCarbs; carbs++) {
      for (let fats = 4; fats <= maxFats; fats++) {
        dosages = [protein, carbs, fats];
        error = factorVectors.reduce(
          (sum, vec, idx) => sum += (Math.abs(dot(dosages, vec) - totalsArray[idx]) / totalsArray[idx])
        , 0);
        // if ([18, 15, 4].every((val, idx) => val === dosages[idx])) {
        //   console.log('error: ' + error);
        // }
        if (error < minError) {
          optimalDosages = [...dosages];
          minError = error;
        }
      }
    }
  }
  // console.log({
  //   optimalDosages,
  //   errors: [...factorVectors.map((val, idx) => dot(optimalDosages, val) - totalsArray[idx]), minError],
  // });
  $('#optimal_protein').text(optimalDosages[0]);
  $('#optimal_carbs').text(optimalDosages[1]);
  $('#optimal_fats').text(optimalDosages[2]);
}

function dot(a, b) {
  if (a.length !== b.length) {
    throw 'Different length vectors were provided for dot product.';
  }
  return a.reduce((sum, val, idx) => sum + val * b[idx], 0);
}

function measurePerformance(callback, calls=10) {
  var t0 = performance.now();
  for (let i = 0; i < calls; i++) {
    callback();
  }
  var t1 = performance.now();
  console.log(calls + ' calls took ' + (t1 - t0) + ' milliseconds.');
}
