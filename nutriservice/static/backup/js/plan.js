const { gender, age, height, weight, body_fat: bodyFat, pal, pal_map: palMap } = jsContext;
const BMR_CONSTANT = 6.25*height - 5*age + { m: 5, f: -161 }[gender];

let tmp = null;

function measurePerformance(callback, calls=10) {
  var t0 = performance.now();
  for (let i = 0; i < calls; i++) {
    callback();
  }
  var t1 = performance.now();
  console.log(calls + ' calls took ' + (t1 - t0) + ' milliseconds.');
}

function properRound(value, places) {
  const multiplier = 10 ** places;
  return Math.round(value * multiplier) / multiplier;
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

function dot(a, b) {
  if (a.length !== b.length) {
    throw 'Different length vectors were provided for dot product.';
  }
  return a.reduce((sum, val, idx) => sum + val * b[idx], 0);
}

function findDosages(totals, initialDosages) {
  for (let arg in [totals, initialDosages]) {
    for (let key in arg) {
      if (typeof arg[key] === 'undefined' || (typeof arg[key] === 'number' && Number.isNaN(arg[key]))) {
        return;
      }
    }
  }
  
  let { totalProteins, totalCarbs, totalFats } = totals;
  const { regularMilk, lowFatMilk, fruit, vegetables } = initialDosages;
  const initialDosagesArray = [regularMilk, lowFatMilk, fruit, vegetables];

  totalProteins -= dot(initialDosagesArray, [7, 7, 0, 2]);
  totalCarbs -= dot(initialDosagesArray, [12, 10, 10, 5]);
  totalFats -= dot(initialDosagesArray, [4, 1.2, 0, 0]);
  const totalsArray = [totalProteins, totalCarbs, totalFats];

  const maxProteins = Math.ceil(Math.min(totalProteins / 7, totalFats / 3));
  const maxCarbs = Math.ceil(Math.min(totalProteins / 2, totalCarbs / 15));
  const maxFats = Math.ceil(totalFats / 5);
  
  const factorVectors = [
    [7, 2, 0],
    [0, 15, 0],
    [3, 0, 5],
  ];
  
  let dosages, optimalDosages = null;
  let minError = 1000;

  for (let proteins = 0, error = 0; proteins < maxProteins; proteins++) {
    for (let carbs = 0; carbs < maxCarbs; carbs++) {
      for (let fats = 0; fats < maxFats; fats++) {
        dosages = [proteins, carbs, fats];
        error = factorVectors.reduce(
          (sum, vec, idx) => sum += Math.abs(dot(dosages, vec) - totalsArray[idx])
        , 0);
        if (error < minError) {
          optimalDosages = [...dosages];
          minError = error;
        }
      }
    }
  }
  // console.log({
  //   optimalDosages,
  //   errors: factorVectors.map((val, idx) => dot(optimalDosages, val) - totalsArray[idx]),
  // });
  $('#optimal_proteins').text(optimalDosages[0]);
  $('#optimal_carbs').text(optimalDosages[1]);
  $('#optimal_fats').text(optimalDosages[2]);
}
/* findDosages({
  totalProteins: 156,
  totalCarbs: 313,
  totalFats: 69,
}, {
  regularMilk: 0,
  lowFatMilk: 3,
  vegetables: 3,
  fruit: 3,
}); */

function render() {  //TODO try without parseFloat
  const goalWeight = parseFloat($('#goal_weight_efield input').val());
  const goalBodyFat = parseFloat($('#goal_body_fat_efield input').val());
  const newPal = $('#new_pal_efield select').val();
  
  const goalTime = parseFloat($('#goal_time_efield input').val());
  const palChange = parseFloat($('#pal_change_efield input').val());
  const goalDailyEnergy = parseFloat($('#goal_daily_energy_efield input').val());

  const regularMilk = parseInt($('#regular_milk_efield input').val());
  const lowFatMilk = parseInt($('#low_fat_milk_efield input').val());
  const fruit = parseInt($('#fruit_efield input').val());
  const vegetables = parseInt($('#vegetables_efield input').val());

  const proteins = parseFloat($('#proteins_efield input').val()) / 100;
  const carbs = parseFloat($('#carbs_efield input').val()) / 100;
  const fats = parseFloat($('#fats_efield input').val()) / 100;

  const proteinsWeight = Math.round(goalDailyEnergy * proteins / 4);
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
  $('#fruit').text(fruit);
  $('#vegetables').text(vegetables);
  
  // Update computed fields
  $('#goal_weight_extra').text(getSignal(goalWeight - weight) + ' kg');
  $('#goal_body_fat_extra').text(getSignal(goalBodyFat - bodyFat) + ' %');
  $('#new_pal_extra').text('PAL ' + newPal);
  
  setTimeout(() => niddk({
      ...jsContext,
      gender: { m: 'Male', f: 'Female' }[gender],
      pal: parseFloat(pal),
      goalWeight: goalWeight,
      goalTime: goalTime * 30,
      palChange: palChange,
    })
  );
  
  $('#goal_bmi').text(properRound(goalWeight / (height / 100) ** 2, 1));
  const goalBmr = 10 * goalWeight + BMR_CONSTANT;
  $('#goal_bmr').text(Math.round(goalBmr));
  $('#goal_daily_energy_extra').text(Math.round(goalBmr * newPal) + ' kcal/dia');

  $('#proteins_weight').text(proteinsWeight);
  $('#carbs_weight').text(carbsWeight);
  $('#fats_weight').text(fatsWeight);

  $('#proteins_per_weight').text(properRound(proteinsWeight / weight, 2));
  $('#carbs_per_weight').text(properRound(carbsWeight / weight, 2));
  $('#fats_per_weight').text(properRound(fatsWeight / weight, 2));

  setTimeout(() => findDosages({
    totalProteins: proteinsWeight,
    totalCarbs: carbsWeight,
    totalFats: fatsWeight,
  }, {
    regularMilk: regularMilk,
    lowFatMilk: lowFatMilk,
    fruit: fruit,
    vegetables: vegetables,
  }));
}

function addEventListeners() {
  $('.efield .field-value').click(function edit() {
    tmp = $(this).parent().hide()
        .siblings('.efield-controls').show()
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
  
  // $('.efield-cancel').click(function(event) {
  //   event.preventDefault();
  //   cancel(this);
  // });

  $('.efield input[type!="range"], .efield select').blur(function() {
    if (!event.relatedTarget || !event.relatedTarget.classList.contains('efield-save')) {
      cancel(this);
    }
  }).keydown(function(event) {
    if (event.key === 'Enter') save(this, $(this).val());
    else if (event.key === 'Escape') cancel(this);
  });

  $('.efield input[type="range"]').on('input', function() {
    $(this).parent().siblings('.field-extra').text($(this).val());
  });

  $('.efield input[type="range"]').change(render);

  // Range inputs interdependence
  const mns = ['proteins', 'carbs', 'fats', 'proteins', 'carbs'].map(mn => $(`#${mn}_efield input`));
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

function init() {
  // Hide efield controls
  $('.efield-controls').hide();

  // Set range input label values
  $('.efield input[type="range"]').each(function() {
    $(this).parent().siblings('.field-extra').text($(this).val());
  });

  // Set constant field values
  $('#pal_extra').text('PAL ' + pal);
  $('#bmi').text(properRound(weight / (height / 100) ** 2, 1));
  const bmr = 10 * weight + BMR_CONSTANT;
  $('#bmr').text(Math.round(bmr));
  $('#daily_energy').text(Math.round(bmr * pal));
  
  render();

  addEventListeners();
}
init();
