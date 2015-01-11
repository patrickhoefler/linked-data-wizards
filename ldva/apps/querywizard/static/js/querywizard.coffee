###
Copyright (C) 2014 Kompetenzzentrum fuer wissensbasierte Anwendungen und Systeme
Forschungs- und Entwicklungs GmbH (Know-Center), Graz, Austria
office@know-center.at

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
###


# CoffeeScripts and jQueries and Promises, oh my :)
$ ->

  ###
  Set global constants
  ###
  $('body').data('DEBUG', false)
  $('body').data('BATCH_SIZE', 10)
  $('body').data('BIG_LOAD_SIZE', 100)

  $('body').data('ERROR_CANNOT_REMOVE_LAST_FILTER',
    """
    This is the last filter.
    Therefore, you cannot remove it.
    Sorry about that.
    """
  )


  ###
  Set global variables
  ###
  $('body').data('xhrPool', [])


  ###
  Initialize data structures
  ###
  $('body').data('endpoint', '')
  $('body').data('search_type', 'regex')
  $('body').data('subjects', [])
  $('body').data('predicates', [])
  $('body').data('dataset', '')
  $('body').data('dimensions', {})
  $('body').data('measures', {})
  $('body').data('total_results_count', 0)


  ###
  Register event handlers
  ####

  # Events - Search
  $.address.externalChange(url_change_handler)
  $(document).on(
    'submit', '#search_form', submit_search_form_handler
  )
  $(document).on(
    'click', 'th .add_not_empty_filter', add_not_empty_filter_handler
  )
  $(document).on(
    'click', 'th .add_date_filter', edit_date_filter_handler
  )
  $(document).on(
    'click', 'th .add_datetime_filter', edit_datetime_filter_handler
  )
  $(document).on(
    'click', 'th .add_numeric_filter', edit_numeric_filter_handler
  )
  $(document).on(
    'click', 'th .add_search_filter', edit_search_filter_handler
  )
  $(document).on(
    'click', 'td .add_uri_filter', add_uri_filter_handler
  )
  $(document).on(
    'click', 'th .edit_date_filter', edit_date_filter_handler
  )
  $(document).on(
    'click', 'th .edit_datetime_filter', edit_datetime_filter_handler
  )
  $(document).on(
    'click', 'th .edit_numeric_filter', edit_numeric_filter_handler
  )
  $(document).on(
    'submit', '#date_filter_modal form', submit_edit_date_filter_handler
  )
  $(document).on(
    'submit', '#datetime_filter_modal form',
    submit_edit_datetime_filter_handler
  )
  $(document).on(
    'submit', '#numeric_filter_modal form',
    submit_edit_numeric_filter_handler
  )
  $(document).on(
    'click', 'th .edit_search_filter', edit_search_filter_handler
  )
  $(document).on(
    'submit', '#search_filter_modal form',
    submit_edit_search_filter_handler
  )
  $(document).on(
    'click', 'th .remove_filter', remove_filter_handler
  )
  $(document).on(
    'click', 'td .focus', focus_handler
  )

  # Events - Data Management
  $(document).on(
    'click', '.add_predicate', add_column_handler
  )
  $(document).on(
    'click', '#load_more button', load_more_results_handler
  )
  $(document).on(
    'click', '.remove_predicate', remove_column_handler
  )
  $(document).on(
    'click', '#aggregate_create', create_aggregated_dataset_handler
  )

  # Events - UI
  $(document).on(
    'change', '#dataset_endpoint_selector',
    ui_change_dataset_endpoint_selector_handler
  )
  $(document).on(
    'click', '.cube_info', ui_dummy_cube_info_handler
  )
  $(document).on(
    'hidden.bs.modal', '#screencast_modal',
    ui_hide_screencast_modal_handler
  )
  $(document).on(
    'shown.bs.modal', '#date_filter_modal',
    ui_date_filter_modal_shown_handler
  )
  $(document).on(
    'shown.bs.modal', '#datetime_filter_modal',
    ui_datetime_filter_modal_shown_handler
  )
  $(document).on(
    'shown.bs.modal', '#numeric_filter_modal',
    ui_numeric_filter_modal_shown_handler
  )
  $(document).on(
    'shown.bs.modal', '#search_filter_modal',
    ui_search_filter_modal_shown_handler
  )
  $(document).on(
    'shown.bs.modal', '#dataset_metadata_modal',
    ui_dataset_metadata_modal_shown_handler
  )
  $(document).on(
    'shown.bs.modal', '#mindmap_metadata_modal',
    ui_mindmap_metadata_modal_shown_handler
  )
  $(document).on(
    'show.bs.modal', '#mm_modal', ui_mm_modal_handler
  )
  $(document).on(
    'show.bs.modal', '#screencast_modal',
    ui_show_screencast_modal_handler
  )
  $(document).on(
    'show.bs.modal', '#sparql_runtime_modal',
    ui_sparql_runtime_modal_show_handler
  )
  $(document).on(
    'show.bs.modal', '#jsonld_modal',
    ui_jsonld_modal_show_handler
  )
  $(document).on(
    'click', '#menu_aggregate_dataset a',
    ui_show_aggregate_modal_handler
  )
  $(document).on(
    'click', '#menu_save_data_to_42 a',
    ui_show_save_data_to_42_modal_handler
  )
  $(document).on(
    'click', '#menu_save_query_to_42 a',
    ui_show_save_query_to_42_modal_handler
  )
  $(document).on(
    'click', '#menu_vis_generic a',
    ui_show_vis_generic_modal_handler
  )
  $(document).on(
    'change', '#aggregate_dimensions input',
    ui_validate_aggregate_dimensions_handler
  )
  $(document).on(
    'change', '#aggregate_measures select',
    ui_validate_aggregate_measures_handler
  )
  $(document).on(
    'keyup', '#dataset_metadata_modal input',
    ui_validate_dataset_metadata_handler
  )
  $(document).on(
    'keyup', '#dataset_metadata_modal textarea',
    ui_validate_dataset_metadata_handler
  )
  $(document).on(
    'keyup', '#mindmap_metadata_modal input',
    ui_validate_mindmap_metadata_handler
  )
  $(document).on(
    'click', '#aggregate_more_values',
    ui_aggregate_more_values_handler
  )
  $(document).on(
    'click', '.group_by_column',
    ui_group_by_column_handler
  )
  $(document).on(
    'click', '.sparql_toggle',
    ui_sparql_toggle_handler
  )

  # Events - External
  $(document).on(
    'click', '#login', external_login_handler
  )
  $(document).on(
    'click', '#menu_vis_dataset a', external_vis_dataset_handler
  )
  $(document).on(
    'submit', '#dataset_metadata_modal form',
    external_save_and_redirect_handler
  )
  $(document).on(
    'submit', '#mindmap_metadata_modal form',
    external_mindmap_metadata_submit_handler
  )
  $(document).on(
    'click', '#dataset_list .compare', dataset_compare_checkbox_click
  )
  $(document).on(
    'click', '#viscompare_button', dataset_compare_viswizard_click
  )

  ###
  Collect all outstanding AJAX requests in an xhrPool
  ###

  # When an AJAX request is sent, add it to the xhrPool
  $(document).ajaxSend(
    (event, jqXHR, options) ->
      $('body').data('xhrPool').push(jqXHR)
      debug "#{$('body').data('xhrPool').length} AJAX call(s) in progress"
  )

  # When an AJAX request is finished, remove it from the xhrPool
  $(document).ajaxComplete(
    (event, jqXHR, options) ->
      xhrIndex = $('body').data('xhrPool').indexOf(jqXHR)
      if xhrIndex > -1
        $('body').data('xhrPool').splice(xhrIndex, 1)
      debug "#{$('body').data('xhrPool').length} AJAX call(s) in progress"
  )


###
Event Handlers - Search
###

# Something has externally changed the address:
# * User has loaded the page for the first time
# * User has pressed the back or forward button of the browser
url_change_handler = (event) ->
  abort_all_ajax_calls()

  # Clear data structures
  $('body').data('dataset', '')
  $('body').data('endpoint', '')
  $('body').data('search_type', 'regex')
  $('body').data('dimensions', {})
  $('body').data('measures', {})
  $('body').data('predicates', [])
  $('body').data('subjects', [])
  $('ul#available_predicates').empty()
  $('#dataset_title_input').val('')
  $('#dataset_description_input').val('')

  # Prepare the UI
  $('#results_page').hide()
  $('#navbar_container').hide()
  $('#results tr').remove()
  $('#load_more').html('')
  $('#dataset_title').hide()
  $('#add_column').hide()
  $('#results_count').hide()
  ui_clear_spinner()

  # We received no search parameters
  if event.parameterNames.length is 0
    # Set default endpoint for dataset selector
    $('body').data('endpoint', 'http://open-data.europa.eu/en/sparqlep')
    ui_display_the_front_page()

  # The user has come from 42-data.org
  else if 'userId' in event.parameterNames
    login_location = '/qa?target=query&userId=' + event.parameters.userId
    if 'dataset' in event.parameterNames
      login_location += '&dataset=' + event.parameters.endpoint
    if 'endpoint' in event.parameterNames
      login_location += '&endpoint=' + event.parameters.endpoint
    window.location.href = login_location

  # We received search parameters
  else
    # Turn the URL parameters into our internal data structure
    for key, value of event.parameters
      if /^dataset$/.test(key)  # RDF Data Cube dataset URI
        $('body').data('dataset', decodeURIComponent(value))
      else if /^p[0-9]+$/.test(key)  # Predicate URI
        $('body').data('predicates').push({uri: decodeURIComponent(value)})
      else if /^p[0-9]+i$/.test(key)  # Is the predicate inverse (?o ?p ?s)?
        index = key.match(/[0-9]+/)[0]
        $('body').data('predicates')[index]['inverse'] = (
          decodeURIComponent(value) == 'true'
        )
      else if /^p[0-9]+ft$/.test(key)  # Filter type
        index = key.match(/[0-9]+/)[0]
        $('body').data('predicates')[index]['filter_type'] = \
          decodeURIComponent(value)
      else if /^p[0-9]+fv$/.test(key)  # Filter value
        index = key.match(/[0-9]+/)[0]
        $('body').data('predicates')[index]['filter_value'] = \
          decodeURIComponent(value)
      else if /^p[0-9]+fl$/.test(key)  # Filter label
        index = key.match(/[0-9]+/)[0]
        $('body').data('predicates')[index]['filter_label'] = \
          decodeURIComponent(value)
      else if /^endpoint$/.test(key)  # Endpoint URL
        $('body').data('endpoint', decodeURIComponent(value))
      else if /^searchtype$/.test(key)  # Endpoint search type
        $('body').data('search_type', decodeURIComponent(value))

    # Only the endpoint is provided
    if $('body').data('endpoint') and
        not are_we_in_dataset_mode() and
        $('body').data('predicates').length is 0
      ui_display_the_front_page()

    # Let's start the search
    else
      # Set the default endpoint
      if not $('body').data('endpoint')
        $('body').data('endpoint', 'code')

      $.when(
        initial_search()
      )
      .done(
        (data) ->
          debug data
      )


# User has submitted the search form
submit_search_form_handler = (event) ->
  event.preventDefault()

  # Make sure the user has entered a search term
  if not $('#q').val()
    return

  $('body').data('endpoint', $('#ep :selected').val())
  $('body').data('search_type', $('#ep :selected').attr('data-search-type'))

  # Prepare the search term
  search_term = $('#q').val()
  search_term = search_term.replace(/\"/g, '')  # Remove apostrophes
  # If we're searching in regex mode, replace blanks with .*
  if $('body').data('search_type') == 'regex'
    search_term = search_term.replace(/[ ]/g, '.*')

  # Set the default predicates and search filters
  $('body').data('predicates', [])
  label_uri = 'http://www.w3.org/2000/01/rdf-schema#label'
  # FIXME: This shouldn't be hardcoded
  if ($('#ep').val() == 'http://europeana.ontotext.com/sparql' or
      $('#ep').val() == 'http://linkedlifedata.com/sparql')
    label_uri = 'http://purl.org/dc/elements/1.1/title'
  $('body')
    .data('predicates')
    .push({
      'uri': label_uri,
      'inverse': false,
      'filter_type': 'search',
      'filter_value': search_term,
    })
  $('body')
    .data('predicates')
    .push({
      'uri': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
      'inverse': false,
    })

  $.when(
    initial_search()
  )
  .done(
    (data) ->
      debug data
  )


# User has submitted the edit date filter form
submit_edit_date_filter_handler = (event) ->
  # Tell the browser to ignore the form submit
  event.preventDefault()

  abort_all_ajax_calls()

  # Get the index of the predicate that the user wants to filter
  p_index = $('#date_filter_predicate_index').val()

  min = $('#date_filter_input_min').val()
  max = $('#date_filter_input_max').val()

  if min and max
    filter_label = "#{min}–#{max}"
  else if min
    filter_label = "&ge; #{min}"
  else if max
    filter_label = "&le; #{max}"

  # Add the filter to the data structure
  $('body').data('predicates')[p_index]['filter_type'] = 'date'
  $('body').data('predicates')[p_index]['filter_value'] = min + ',' + max
  $('body').data('predicates')[p_index]['filter_label'] = filter_label

  # Add the filter to the table header
  $("th:eq(#{p_index}) .filter").html("""
    <div class="dropdown">
      <button type="button" class="btn btn-default btn-xs dropdown-toggle"
      data-toggle="dropdown">
        <span class="glyphicon glyphicon-filter"></span>
        #{filter_label} <span class="caret"></span>
      </button>
      <ul class="dropdown-menu">
        <li>
          <a href="#" class="edit_date_filter">
            <span class="glyphicon glyphicon-pencil"></span>
            Edit filter &hellip;
          </a>
        </li>
        <li>
          <a href="#" class="remove_filter">
            <span class="glyphicon glyphicon-remove"></span> Remove filter
          </a>
        </li>
      </ul>
    </div>
    """)

  $('#date_filter_modal').modal('hide')

  update_the_address()
  clear_results()

  $.when(
    ui_get_and_display_the_total_results_count()
  )
  .done(
    (data) ->
      debug data
  )

  $.when(
    get_additional_subjects($('body').data('BATCH_SIZE'))
  )
  .done(
    (data) ->
      debug data
  )


# User has submitted the edit datetime filter form
submit_edit_datetime_filter_handler = (event) ->
  # Tell the browser to ignore the form submit
  event.preventDefault()

  abort_all_ajax_calls()

  # Get the index of the predicate that the user wants to filter
  p_index = $('#datetime_filter_predicate_index').val()

  min = $('#datetime_filter_input_min').val()
  max = $('#datetime_filter_input_max').val()
  
  # Workaround for missing seconds
  if min.length == 16
    min += ':00'
  if max.length == 16
    max += ':00'

  if min and max
    filter_label = "#{min}–#{max}"
  else if min
    filter_label = "&ge; #{min}"
  else if max
    filter_label = "&le; #{max}"

  # Add the filter to the data structure
  $('body').data('predicates')[p_index]['filter_type'] = 'datetime'
  $('body').data('predicates')[p_index]['filter_value'] = min + ',' + max
  $('body').data('predicates')[p_index]['filter_label'] = filter_label

  # Add the filter to the table header
  $("th:eq(#{p_index}) .filter").html("""
    <div class="dropdown">
      <button type="button" class="btn btn-default btn-xs dropdown-toggle"
      data-toggle="dropdown">
        <span class="glyphicon glyphicon-filter"></span>
        #{filter_label} <span class="caret"></span>
      </button>
      <ul class="dropdown-menu">
        <li>
          <a href="#" class="edit_datetime_filter">
            <span class="glyphicon glyphicon-pencil"></span>
            Edit filter &hellip;
          </a>
        </li>
        <li>
          <a href="#" class="remove_filter">
            <span class="glyphicon glyphicon-remove"></span> Remove filter
          </a>
        </li>
      </ul>
    </div>
    """)

  $('#datetime_filter_modal').modal('hide')

  update_the_address()
  clear_results()

  $.when(
    ui_get_and_display_the_total_results_count()
  )
  .done(
    (data) ->
      debug data
  )

  $.when(
    get_additional_subjects($('body').data('BATCH_SIZE'))
  )
  .done(
    (data) ->
      debug data
  )


# User has submitted the edit numeric filter form
submit_edit_numeric_filter_handler = (event) ->
  # Tell the browser to ignore the form submit
  event.preventDefault()

  abort_all_ajax_calls()

  # Get the index of the predicate that the user wants to filter
  p_index = $('#numeric_filter_predicate_index').val()

  min = $('#numeric_filter_input_min').val()
  max = $('#numeric_filter_input_max').val()

  if min and max
    filter_label = "#{min}–#{max}"
  else if min
    filter_label = "&ge; #{min}"
  else if max
    filter_label = "&le; #{max}"

  # Add the filter to the data structure
  $('body').data('predicates')[p_index]['filter_type'] = 'numeric'
  $('body').data('predicates')[p_index]['filter_value'] = min + ',' + max
  $('body').data('predicates')[p_index]['filter_label'] = filter_label

  # Add the filter to the table header
  $("th:eq(#{p_index}) .filter").html("""
    <div class="dropdown">
      <button type="button" class="btn btn-default btn-xs dropdown-toggle"
      data-toggle="dropdown">
        <span class="glyphicon glyphicon-filter"></span>
        #{filter_label} <span class="caret"></span>
      </button>
      <ul class="dropdown-menu">
        <li>
          <a href="#" class="edit_numeric_filter">
            <span class="glyphicon glyphicon-pencil"></span>
            Edit filter &hellip;
          </a>
        </li>
        <li>
          <a href="#" class="remove_filter">
            <span class="glyphicon glyphicon-remove"></span> Remove filter
          </a>
        </li>
      </ul>
    </div>
    """)

  $('#numeric_filter_modal').modal('hide')

  update_the_address()
  clear_results()

  $.when(
    ui_get_and_display_the_total_results_count()
  )
  .done(
    (data) ->
      debug data
  )

  $.when(
    get_additional_subjects($('body').data('BATCH_SIZE'))
  )
  .done(
    (data) ->
      debug data
  )


# User has submitted the edit search filter form
submit_edit_search_filter_handler = (event) ->
  # Tell the browser to ignore the form submit
  event.preventDefault()

  # Hide the modal window
  $('#search_filter_modal').modal('hide')

  # Get the index of the predicate that the user wants to filter
  p_index = $('#search_filter_predicate_index').val()

  # Add the filter to the data structure
  $('body').data('predicates')[p_index]['filter_type'] = 'search'
  $('body').data('predicates')[p_index]['filter_value'] = \
    $('#search_filter_input').val()

  # Update the search term in the UI
  $('th').eq(p_index).find('.filter').html(
    """
      <div class="dropdown">
        <button type="button" class="btn btn-default btn-xs dropdown-toggle"
        data-toggle="dropdown">
          <span class="glyphicon glyphicon-filter"></span>
          "#{$('#search_filter_input').val()}" <span class="caret"></span>
        </button>
        <ul class="dropdown-menu">
          <li>
            <a href="#" class="edit_search_filter"><span
            class="glyphicon glyphicon-pencil"></span> Edit filter &hellip;</a>
          </li>
          <li>
            <a href="#" class="remove_filter"><span
            class="glyphicon glyphicon-remove"></span> Remove filter</a>
          </li>
        </ul>
      </div>
    """
  )

  update_the_address()
  clear_results()

  $.when(
    ui_get_and_display_the_total_results_count()
  )
  .done(
    (data) ->
      debug data
  )

  $.when(
    get_additional_subjects($('body').data('BATCH_SIZE'))
  )
  .done(
    (data) ->
      debug data
  )


# User wants to add a "not empty" filter
add_not_empty_filter_handler = (event) ->
  # Tell the browser to ignore the click on the link
  event.preventDefault()

  abort_all_ajax_calls()

  # Get the index of the predicate that the user wants to filter
  predicate_index = $(event.target).closest("th").prevAll("th").length

  # Add the filter to the data structure
  $('body').data('predicates')[predicate_index]['filter_type'] = 'not_empty'
  $('body').data('predicates')[predicate_index]['filter_value'] = 1

  # Add the filter to the table header
  $("th:eq(#{predicate_index}) .filter").html("""
    <div class="dropdown">
      <button type="button" class="btn btn-default btn-xs dropdown-toggle"
      data-toggle="dropdown">
        <span class="glyphicon glyphicon-filter"></span>
        Hide empty results <span class="caret"></span>
      </button>
      <ul class="dropdown-menu">
        <li>
          <a href="#" class="remove_filter">
            <span class="glyphicon glyphicon-remove"></span> Remove filter
          </a>
        </li>
      </ul>
    </div>
    """)

  # Remove the filter entry from the menu
  $("th:eq(#{predicate_index}) .title .not_empty_filter").remove()

  update_the_address()
  clear_results()

  $.when(
    ui_get_and_display_the_total_results_count()
  )
  .done(
    (data) ->
      debug data
  )

  $.when(
    get_additional_subjects($('body').data('BATCH_SIZE'))
  )
  .done(
    (data) ->
      debug data
  )


# User wants to add a URI filter
add_uri_filter_handler = (event) ->
  # Tell the browser to ignore the click on the link
  event.preventDefault()

  abort_all_ajax_calls()

  # Get the index of the predicate that the user wants to filter
  predicate_index = $(this).closest("td").prevAll("td").length

  # Add the filter to the data structure
  $('body').data('predicates')[predicate_index]['filter_type'] = 'uri'
  $('body').data('predicates')[predicate_index]['filter_value'] = \
    $(this).parent().parent().siblings('button').first().attr('data-uri')
  $('body').data('predicates')[predicate_index]['filter_label'] = \
    $(this).parent().parent().siblings('button').first().text().trim()

  # Add the filter to the table header
  $("th[data-uri=\"#{$(this).closest('td').attr('data-p')}\"] .filter").html("""
    <div class="dropdown">
      <button type="button" class="btn btn-default btn-xs dropdown-toggle"
      data-toggle="dropdown">
        <span class="glyphicon glyphicon-filter"></span>
        #{$(this).parent().parent().siblings('button').first().text()}
        <span class="caret"></span>
      </button>
      <ul class="dropdown-menu">
        <li>
          <a href="#" class="remove_filter"><span
          class="glyphicon glyphicon-remove"></span> Remove filter</a>
        </li>
      </ul>
    </div>
    """)

  update_the_address()
  clear_results()

  $.when(
    ui_get_and_display_the_total_results_count()
  )
  .done(
    (data) ->
      debug data
  )

  $.when(
    get_additional_subjects($('body').data('BATCH_SIZE'))
  )
  .done(
    (data) ->
      debug data
  )


# User wants to remove a filter
remove_filter_handler = (event) ->
  # Tell the browser to ignore the click on the link
  event.preventDefault()

  # This is the last filter and we're not in dataset mode
  if count_filters() is 1 and not are_we_in_dataset_mode()
    alert($('body').data('ERROR_CANNOT_REMOVE_LAST_FILTER'))

  # This is not the last filter and / or we're in dataset mode
  else
    p_index = $(this).closest("th").prevAll("th").length

    # If it was a "not empty filter", add the menu entry again
    if $('body').data('predicates')[p_index]['filter_type'] == 'not_empty'
      $("th:eq(#{p_index}) .title ul").prepend(
        """
          <li class="not_empty_filter">
            <a href="#" class="add_not_empty_filter">
              <span class="glyphicon glyphicon-filter"></span>
              Hide empty results
            </a>
          </li>
        """
      )

    # Remove the filter from the data structure
    delete $('body').data('predicates')[p_index]['filter_type']
    delete $('body').data('predicates')[p_index]['filter_value']
    delete $('body').data('predicates')[p_index]['filter_label']

    # Remove label filter from header
    $(this).closest('th').find('.filter').html('')

    update_the_address()
    clear_results()

    $.when(
      ui_get_and_display_the_total_results_count()
    )
    .done(
      (data) ->
        debug data
    )

    $.when(
      get_additional_subjects($('body').data('BATCH_SIZE'))
    )
    .done(
      (data) ->
        debug data
    )


# User wants to focus on another URI
focus_handler = (event) ->
  # Tell the browser to ignore the click on the link
  event.preventDefault()


###
Event Handlers - Data Management
###

# User wants to add a column
add_column_handler = (event) ->
  # Tell the browser to ignore the click on the link
  event.preventDefault()

  # Add the column
  $.when(
    add_column_for_given_predicate({
      'uri': $(this).data('uri'),
      'inverse': $(this).data('inverse'),
    })
  )
  .done(
    (data) ->
      debug data
  )

  update_the_address()


# User has clicked on the "Load more results" link
load_more_results_handler = (event) ->
  event.preventDefault()

  $('#load_more button').attr('disabled', 'disabled')

  Spinners
    .create(
      event.target,
      {
        radius: 5,
        dashes: 12,
        width: 2,
        height: 5,
        opacity: 1,
        padding: 0,
        rotation: 600,
        color: '#ffffff'
      }
    )
    .play()

  $.when(
    get_additional_subjects($(event.target).attr('data-amount'))
  )
  .done(
    (data) ->
      debug data
  )


# User wants to remove a column
remove_column_handler = (event) ->
  # Tell the browser to ignore the click on the link
  event.preventDefault()

  # Get the index for the column (predicate) the user wants to remove
  predicate_index = $(this).closest("th").prevAll("th").length

  # This column has the last active filter and we're not in dataset mode,
  # alert the user and do nothing
  if count_filters() == 1 and
      $('body').data('predicates')[predicate_index]['filter_value'] and
      not are_we_in_dataset_mode()
    alert($('body').data('ERROR_CANNOT_REMOVE_LAST_FILTER'))

  # Go ahead and remove the column
  else
    # Remove respective th and td's
    $("#results th:eq(#{predicate_index})").remove()
    $("#results tr").each(
      (index, tr) ->
        $(tr).find("td:eq(#{predicate_index})").remove()
    )

    # Add the removed predicate to the list of available predicates
    $('#available_predicates').append(
      """
      <li>
        <a
          class="add_predicate"
          data-label="#{$(this).closest('th').attr('data-label')}"
          data-uri="#{$(this).closest('th').attr('data-uri')}"
          data-inverse="#{$(this).closest('th').attr('data-inverse')}"
          title="#{$(this).closest('th').attr('data-uri')}"
          href="#">#{$(this).closest('th').attr('data-label')}</a>
      </li>
      """
    )

    # Sort the list of available predicates
    listitems = $('#available_predicates').children('li').get().sort(
      (a, b) ->
        $(a).text().toUpperCase().localeCompare(
          $(b).text().toUpperCase()
        )
    )
    for item in listitems
      $('#available_predicates').append(item)

    # Remove the predicate from the data structure
    predicate = $('body').data('predicates').splice(predicate_index, 1)

    update_the_address()

    # Reload column if it had an active filter
    if predicate[0]['filter_value']
      clear_results()

      $.when(
        ui_get_and_display_the_total_results_count()
      )
      .done(
        (data) ->
          debug data
      )

      $.when(
        get_additional_subjects($('body').data('BATCH_SIZE'))
      )
      .done(
        (data) ->
          debug data
      )


# User wants to create an aggregated dataset
create_aggregated_dataset_handler = (event) ->
  $('#aggregate_create').attr('disabled', 'disabled')

  Spinners
    .create(
      $('#aggregate_modal .spinner'),
      {
        radius: 5,
        dashes: 12,
        width: 2,
        height: 6,
        opacity: 1,
        padding: 0,
        rotation: 600,
        color: '#000000'
      }
    )
    .play()

  grouped_dimensions = []
  for checkbox in $('#aggregate_dimensions input:checked')
    grouped_dimensions.push({
      uri: $(checkbox).val(),
      label: $(checkbox).attr('data-label'),
    })

  aggregated_measures = []
  for div in $('#aggregate_measures div')
    if $(div).find('select.agg_function[value!="{}"]').length > 0
      aggregated_measure = \
        JSON.parse($(div).find('select.agg_measure').first().val())
      aggregated_measure['function'] = \
        $(div).find('select.agg_function').first().val()
      aggregated_measures.push(aggregated_measure)

  $.when(
    $.ajaxQueue({
      url: '/query/aggregate',
      type: 'POST',
      data: JSON.stringify({
        dataset_uri: $('body').data('dataset'),
        endpoint_url: $('body').data('endpoint'),
        search_type: $('body').data('search_type'),
        grouped_dimensions: grouped_dimensions,
        aggregated_measures: aggregated_measures,
        label: 'Aggregation of: ' + $('#dataset_label').text(),
        description: '',
        importer: $('#cubify_mendeley_id').val(),
        relation: 'Query Wizard',
        source: window.location.href,
      })
    })
  )
  .done(
    (data) ->
      $('#aggregate_modal').modal('hide')
      redirect_location = '/search#?dataset=' + data.dataset
      redirect_location += '&endpoint=' + data.endpoint
      window.location.href = redirect_location
  )


###
Event Handlers - UI
###

# User wants more aggregated values
ui_aggregate_more_values_handler = (event) ->
  $('#aggregate_measures div')
    .first()
    .clone()
    .appendTo($('#aggregate_measures'))

# User has changed the dataset endpoint
ui_change_dataset_endpoint_selector_handler = (event) ->
  $('body').data('endpoint', event.target.value)

  $.address.history(false)
  update_the_address()
  $.address.history(true)

  get_and_display_the_datasets_of_the_selected_endpoint()


# User clicks on the dimension info entry
ui_dummy_cube_info_handler = (event) ->
  # Tell the browser to ignore the click on the link
  event.preventDefault()


# User wants go group by a certain column
ui_group_by_column_handler = (event) ->
  # Tell the browser to ignore the click on the link
  event.preventDefault()

  ui_show_aggregate_modal(
    $(event.target).closest('th').attr('data-uri')
  )


# User has closed the screencast modal
ui_hide_screencast_modal_handler = (event) ->
  $('#screencast_modal_body').html('')


# User has clicked the "MindMap!" link
ui_mm_modal_handler = (event) ->
  # Turn the results table into a MindMeister-compatible JSON structure
  mm_json = {
    'map_version': '2.2',
    'keep_aligned': true,
    'root': {
      'title': $('#mindmap_title_input').val().trim(),
      'children': [],
    }
  }

  headers = []
  header_row = $('#results tr:first').clone()
  header_row.find('.filter').remove()
  for header, i in $(header_row).find('.title button')
    headers[i] = $(header).text().trim()

  # How many subjects are there?
  root_child_count = $('#results tr:gt(0)').length
  # Iterate through the subjects
  for row, row_index in $('#results tr:gt(0)')
    # Select the first cell in the current row
    for cell in $(row).find('td:first')
      if row_index < (root_child_count / 2)
        xpos = 10
        ypos = 10 * row_index
      else
        xpos = -10
        ypos = 10 * (root_child_count - row_index)

      if $(cell).find('button').length > 0
        for button in $(cell).find('button').first()
          # Add a node for the first button (there should be only one)
          mm_json['root']['children'].push({
            'title': $(button).text().trim(),
            'pos': [xpos, ypos],
            'children': []
          })
      else
        mm_json['root']['children'].push({
          'title': $(cell).text().trim(),
          'pos': [xpos, ypos],
          'children': []
        })
    # Select all other cells in the current row
    for cell, i in $(row).find('td:gt(0)')
      # Add node for current predicate
      mm_json.root.children[mm_json.root.children.length - 1].children.push({
        'title': headers[i + 1],
        'children': []
      })
      # Iterate through objects
      if $(cell).find('button').length > 0
        for button in $(cell).find('button')
          # Add a node for each object
          # Wow, this is ugly
          mm_json.root.children[mm_json.root.children.length - 1].children[mm_json.root.children[mm_json.root.children.length - 1].children.length - 1].children.push({
            'title': $(button).text().trim()
          })
      else
        for entry in $(cell).text().trim().split("\n")
          # Workaround: MindMeister doesn't like empty nodes
          entry = "-" if not entry
          # Add a node for each object
          # And again: Ugly, ugly, ugly
          mm_json.root.children[mm_json.root.children.length - 1].children[mm_json.root.children[mm_json.root.children.length - 1].children.length - 1].children.push({
            'title': entry.trim()
          })

  # Clean the html target
  $('#mm_modal_body').html('')

  # Create the mind map
  MM.init(
    "9fc50d8e8742c8b163512483b1f839f2",
    "https://www.mindmeister.com",
    "mm_modal_body",
    mm_json
  )


# User has clicked the screencast link
ui_show_screencast_modal_handler = (event) ->
  $('#screencast_modal_body').html("""
    <iframe width="853" height="480"
      src="http://www.youtube.com/embed/0LZ87yj5jo8"
      frameborder="0" allowfullscreen></iframe>
    """)


# User has clicked the aggregate dataset link
ui_show_aggregate_modal_handler = (event) ->
  # Tell the browser to ignore the click on the link
  event.preventDefault()

  ui_show_aggregate_modal()


ui_show_aggregate_modal = (group_by_uri) ->
  Spinners.remove($('#aggregate_modal .spinner'))

  $('#aggregate_modal').modal('show')

  # Empty the containers
  $('#aggregate_measures').empty()
  $('#aggregate_dimensions').empty()

  # Display the error messages
  $('#aggregate_dimension_error').show()
  $('#aggregate_measure_error').show()

  # Disable the submit button
  $('#aggregate_create').prop('disabled', true)

  # Add dimensions to UI
  dimension_list = []
  for dimension_uri, dimension of $('body').data('dimensions')
    dimension_list.push({
      uri: dimension_uri,
      label: dimension['label']
    })

  dimension_list = dimension_list.sort(
    (a, b) ->
      if (a.label.toLowerCase() > b.label.toLowerCase())
        return 1
      if (a.label.toLowerCase() < b.label.toLowerCase())
        return -1
      # a is equal to b
      return 0
  )

  for dimension in dimension_list
    $('#aggregate_dimensions').append("""
    <div class="checkbox">
      <label>
        <input type="checkbox" data-label='#{dimension.label}'
        value='#{dimension.uri}'> #{dimension.label}
      </label>
    </div>
      """)

  # Add measures to UI
  measure_list = []
  for measure_uri, measure of $('body').data('measures')
    measure_list.push({
      uri: measure_uri,
      label: measure['label']
    })

  measure_list = measure_list.sort(
    (a, b) ->
      if (a.label.toLowerCase() > b.label.toLowerCase())
        return 1
      if (a.label.toLowerCase() < b.label.toLowerCase())
        return -1
      # a is equal to b
      return 0
  )

  measure_selector = """
  <select class="form-control input-sm agg_measure"
  style="width: 160px; display: inline-block;">
  """

  for measure in measure_list
    measure_selector += """
      <option value='{"uri": "#{measure.uri}",
      "label": "#{measure.label}"}'>#{measure.label}</option>
    """

  measure_selector += """
  </select>
  """

  $('#aggregate_measures').append("""
  <div style="margin-top: 10px;">
    <select class="form-control input-sm agg_function"
    style="width: 100px; display: inline-block;">
      <option value='{}'>-</option>
      <option value='avg'>Average</option>
      <option value='count'>Count</option>
      <option value='max'>Maximum</option>
      <option value='min'>Minimum</option>
      <option value='sum'>Sum</option>
    </select> of
    #{measure_selector}
  </div>
  """)

  if group_by_uri
    $("#aggregate_dimensions input[value='#{group_by_uri}']").prop(
      'checked', true
    )
    ui_validate_aggregate_dimensions_handler()


ui_show_save_data_to_42_modal_handler = (event) ->
  event.preventDefault()
  $('#dataset_redirect').val('qa')
  $('#dataset_payload_type').val('data')
  $('#dataset_metadata_modal').modal('show')


ui_show_save_query_to_42_modal_handler = (event) ->
  event.preventDefault()
  $('#dataset_redirect').val('qa')
  $('#dataset_payload_type').val('query')

  $.ajax({
    url: '/query/get_comprehensive_sparql_query',
    type: 'POST',
    data: JSON.stringify({
      endpoint_url: $('body').data('endpoint'),
      search_type: $('body').data('search_type'),
      predicates: $('body').data('predicates'),
      dataset: $('body').data('dataset')
    })
  })
  .done(
    (data) ->
      $('#cubify_sparql_query').val(htmlEncode(data['query']))
      $('#dataset_metadata_modal').modal('show')
  )


ui_show_vis_generic_modal_handler = (event) ->
  event.preventDefault()
  $('#dataset_redirect').val('vis')
  $('#dataset_payload_type').val('data')
  $('#dataset_metadata_modal').modal('show')


# User wants to toggle the SPARQL query display
ui_sparql_toggle_handler = (event) ->
  event.preventDefault()
  current_textarea = $(this).parent().siblings('textarea').first().toggle()
  if current_textarea.is(":visible")
    $(this).find('.arrow').first().html(
      '<span class="glyphicon glyphicon-chevron-down"></span>'
    )
  else
    $(this).find('.arrow').first().html(
      '<span class="glyphicon glyphicon-chevron-right"></span>'
    )


# User wants to edit a date filter
edit_date_filter_handler = (event) ->
  event.preventDefault()

  p_index = $(event.target).closest("th").prevAll("th").length
  $('#date_filter_predicate_index').val(p_index)

  $('#date_filter_modal .target').html(
    "<em>#{$(event.target).closest('th').attr('data-label')}</em>"
  )

  $('#date_filter_input_min').val('')
  $('#date_filter_input_max').val('')

  if ($('body').data('predicates')[p_index]['filter_type'] == 'date' and
      $('body').data('predicates')[p_index]['filter_value'])
    $('#date_filter_input_min').val(
      $('body').data('predicates')[p_index]['filter_value'].split(',')[0]
    )
    $('#date_filter_input_max').val(
      $('body').data('predicates')[p_index]['filter_value'].split(',')[1]
    )

  $('#date_filter_modal').modal('show')


# User wants to edit a date filter
edit_datetime_filter_handler = (event) ->
  event.preventDefault()

  p_index = $(event.target).closest("th").prevAll("th").length
  $('#datetime_filter_predicate_index').val(p_index)

  $('#datetime_filter_modal .target').html(
    "<em>#{$(event.target).closest('th').attr('data-label')}</em>"
  )

  $('#datetime_filter_input_min').val('')
  $('#datetime_filter_input_max').val('')

  if $('body').data('predicates')[p_index]['filter_type'] == 'datetime' and
      $('body').data('predicates')[p_index]['filter_value']
    $('#datetime_filter_input_min').val(
      $('body').data('predicates')[p_index]['filter_value'].split(',')[0]
    )
    $('#datetime_filter_input_max').val(
      $('body').data('predicates')[p_index]['filter_value'].split(',')[1]
    )

  $('#datetime_filter_modal').modal('show')


# User wants to edit a numeric filter
edit_numeric_filter_handler = (event) ->
  event.preventDefault()

  p_index = $(event.target).closest("th").prevAll("th").length
  $('#numeric_filter_predicate_index').val(p_index)

  $('#numeric_filter_modal .target').html(
    "<em>#{$(event.target).closest('th').attr('data-label')}</em>"
  )

  $('#numeric_filter_input_min').val('')
  $('#numeric_filter_input_max').val('')

  if $('body').data('predicates')[p_index]['filter_type'] == 'numeric' and
      $('body').data('predicates')[p_index]['filter_value']
    $('#numeric_filter_input_min').val(
      $('body').data('predicates')[p_index]['filter_value'].split(',')[0]
    )
    $('#numeric_filter_input_max').val(
      $('body').data('predicates')[p_index]['filter_value'].split(',')[1]
    )

  $('#numeric_filter_modal').modal('show')


# The date filter modal has finished loading
ui_date_filter_modal_shown_handler = (event) ->
  $('#date_filter_input_min').select()


# The date filter modal has finished loading
ui_datetime_filter_modal_shown_handler = (event) ->
  $('#datetime_filter_input_min').select()


# The numeric filter modal has finished loading
ui_numeric_filter_modal_shown_handler = (event) ->
  $('#numeric_filter_input_min').select()


# The dataset metadata modal has finished loading
ui_dataset_metadata_modal_shown_handler = (event) ->
  $('#dataset_title_input').select()


# The mindmap metadata modal has finished loading
ui_mindmap_metadata_modal_shown_handler = (event) ->
  $('#mindmap_title_input').select()


ui_jsonld_modal_show_handler = (event) ->
  jsonld = {
    '@graph': [],
  }

  for subject in $('body').data('subjects')
    subject_json = {
      '@id': "#{subject}",
    }
    jsonld['@graph'].push(subject_json)

  # Iterate through the subjects
  for row, row_index in $('#results tr:gt(0)')
    # Select all cells in the current row
    for cell, col_index in $(row).find('td')
      predicate = $('body').data('predicates')[col_index]
      # There's one URI in the cell
      if $(cell).find('button').length == 1
        jsonld['@graph'][row_index][predicate['uri']] = \
          {'@id': $(cell).find('button').first().attr('data-uri')}
      
      # There are multiple URIs in the cell
      else if $(cell).find('button').length > 1
        uri_list = []
        for button in $(cell).find('button')
          uri_list.push({'@id': $(button).attr('data-uri')})
        jsonld['@graph'][row_index][predicate['uri']] = uri_list
      
      # There's no URI and hopefully only one value in the cell
      else
        if predicate['cube_component_type'] == 'measure'
          jsonld['@graph'][row_index][predicate['uri']] = \
            Number($(cell).text().trim().replace(/\,/g,''))
        else
          jsonld['@graph'][row_index][predicate['uri']] = $(cell).text().trim()

  $('#jsonld textarea').html(JSON.stringify(jsonld, null, 2))


# The sparql runtime modal is loading
ui_sparql_runtime_modal_show_handler = (event) ->
  if $('body').data('endpoint')
    $('#sparql_endpoint').html("""
    <div style="font-weight: bold;">Current SPARQL endpoint</div>
    <a href="#{$('body').data('endpoint')}"
    target="_blank">#{$('body').data('endpoint')}</a>
    <hr />
    """)
  $.ajax({
    url: '/query/get_comprehensive_sparql_query',
    type: 'POST',
    data: JSON.stringify({
      endpoint_url: $('body').data('endpoint'),
      search_type: $('body').data('search_type'),
      predicates: $('body').data('predicates'),
      dataset: $('body').data('dataset')
    })
  })
  .done(
    (data) ->
      $('#sparql_query').html("""
        <div style="font-weight: bold;">SPARQL query for the current
        selection</div>
        <textarea readonly="readonly" style="width: 100%; height: 200px;
        margin: 5px 0 10px 0;">#{htmlEncode(data['query'])}</textarea>
        <hr />
      """)
  )


# User wants to edit a search filter
edit_search_filter_handler = (event) ->
  event.preventDefault()
  $('#search_filter_predicate_index').val(
    $(event.target).closest("th").prevAll("th").length
  )
  $('#search_filter_modal .target').html(
    "<em>#{$(event.target).closest('th').attr('data-label')}</em>"
  )
  $('#search_filter_input').val(
    $(event.target).closest('.filter').find('button').first().text(
    ).replace(/\"/g, '').trim()
  )
  $('#search_filter_modal').modal('show')


# The search filter modal has finished loading
ui_search_filter_modal_shown_handler = (event) ->
  $('#search_filter_input').select()


ui_validate_aggregate_dimensions_handler = (event) ->
  dimensions_count = Object.keys($('body').data('dimensions')).length
  checked_dimensions = $('#aggregate_dimensions input:checked').length
  if 0 < checked_dimensions < dimensions_count
    $('#aggregate_dimension_error').hide()
    if not $('#aggregate_measure_error').is(':visible')
      $('#aggregate_create').prop('disabled', false)
  else
    $('#aggregate_dimension_error').show()
    $('#aggregate_create').prop('disabled', true)


ui_validate_aggregate_measures_handler = (event) ->
  selected = $('#aggregate_measures select.agg_function[value!="{}"]').length
  if selected > 0
    $('#aggregate_measure_error').hide()
    if not $('#aggregate_dimension_error').is(':visible')
      $('#aggregate_create').prop('disabled', false)
  else
    $('#aggregate_measure_error').show()
    $('#aggregate_create').prop('disabled', true)


ui_validate_dataset_metadata_handler = (event) ->
  if not ($('#dataset_title_input').val() and
          $('#dataset_description_input').val())
    $('#dataset_metadata_submit').prop('disabled', true)
  else
    $('#dataset_metadata_submit').prop('disabled', false)


ui_validate_mindmap_metadata_handler = (event) ->
  if not $('#mindmap_title_input').val()
    $('#mindmap_metadata_submit').prop('disabled', true)
  else
    $('#mindmap_metadata_submit').prop('disabled', false)


###
Event Handlers - External Actions
###

external_login_handler = (event) ->
  event.target.href += "?next=" + encodeURIComponent(
    window.location.pathname + window.location.search + window.location.hash
  )


external_prepare_table_for_cubification = () ->
  # Copy the current results table into the form
  results_table = $('#results').clone()

  # Remove multivalue columns
  results_table.find("[data-component='multivalue']").remove()

  # Remove the buttons, but keep the text
  results_table.find('button').each(
    () ->
      $(this).replaceWith($(this).html().trim())
  )

  # Remove all css styles
  results_table.find('*').removeAttr('style')

  # Remove navigation elements, filter information and line breaks
  results_table.find('.dropdown-menu').remove()
  results_table.find('.filter').remove()
  results_table.find('br').remove()

  # Duplicate data-s into data-url attribute
  results_table
    .find('td[data-s]')
    .each(
      (index, td) ->
        $(td).attr('data-url', $(td).attr('data-s'))
    )

  # Workaround: Remove DataSet column
  # Find the column we are looking for
  th = results_table.find("""th[data-uri="http://purl.org/linked-data/cube#dataSet"]""").first()
  if th.length > 0
    # Get the index for the current column (predicate)
    p_index = th.prevAll("th").length
    # Remove the th
    th.remove()
    # Remove all corresponding td's
    results_table
      .find('tr')
      .each(
        (index, tr) ->
          $(tr)
            .find('td:eq(' + p_index + ')')
            .remove()
      )

  # Replace <th> with <td> tags
  results_table
    .find('th')
    .each(
      (index, th) ->
        $(th).replaceWith(
          """
          <td data-url="#{$(th).attr('data-uri')}"
          data-component="#{$(th).attr('data-component')}">
            #{$(th).html().trim()}
          </td>
          """
        )
    )

  # Remove <div>, <span>, and <strong> tags
  results_table
    .find('div')
    .each(
      (index, div) ->
        $(div).replaceWith($(div).html().trim())
    )
  results_table
    .find('span')
    .each(
      (index, span) ->
        $(span).replaceWith($(span).html().trim())
    )
  results_table
    .find('strong')
    .each(
      (index, span) ->
        $(span).replaceWith($(span).html().trim())
    )

  # Add missing <p> tags
  results_table
    .find('td:not(:has(p))')
    .each(
      (index, td) ->
        $(td).html('<p>' + $(td).html().trim() + '</p>')
    )

  # Remove all newlines
  results_table.html(results_table.html().replace(/(\r\n|\n|\r)/gm, ''))

  # Remove all commas from measures
  results_table
    .find('td[data-component="observation"] p')
    .each(
      (index, td) ->
        $(td).html($(td).html().replace(/\,/g, ''))
    )

  # Remove all class attributes
  results_table.find('*').removeAttr('class')

  # Add the wrapping <table> tag
  results_table_html = results_table.clone().wrap('<table>').parent().html()

  # Save the resulting html into the form
  $('#cubify_html_table').val(results_table_html)

  debug results_table_html


# User has clicked the "Visualize!" link and it's a dataset
external_vis_dataset_handler = (event) ->
  # Workaround for https://bugzilla.mozilla.org/show_bug.cgi?id=483304
  event.target.href = "/vis#" + window.location.hash.substring(1).replace(
    /\#/g, '%23'
  )


external_mindmap_metadata_submit_handler = (event) ->
  event.preventDefault()

  if not $('#mindmap_title_input').val()
    return

  $('#mindmap_metadata_modal').modal('hide')
  $('#mm_modal').modal('show')


dataset_compare_checkbox_click = (event) ->
  if $('#dataset_list .compare:checked').length > 0
    $('#viscompare_button').show()
  else
    $('#viscompare_button').hide()

dataset_compare_viswizard_click = (event) ->
  event.preventDefault()
  endpoint = $('body').data('endpoint')
  $datasets = $('#dataset_list .compare:checked');
  url = "/vis#?"
  counter = 0
  if $datasets.length > 0
    $datasets.each((index, jqXHR) ->
      url += "&chart#{counter}=&chartDsIn#{counter}=#{counter}&ds#{counter}e=#{endpoint}&ds#{counter}u=" + $(this).data('dataset')
      counter++
    )
  document.location.href = url;


external_save_and_redirect_handler = (event) ->
  event.preventDefault()

  if not ($('#dataset_title_input').val() and
          $('#dataset_description_input').val())
    return

  $('#cubify_label').val($('#dataset_title_input').val())
  $('#results').attr('data-label', $('#dataset_title_input').val())

  $('#cubify_description').val($('#dataset_description_input').val())
  $('#results').attr('data-description', $('#dataset_description_input').val())

  $('#cubify_source').val(window.location.href)
  $('#results').attr('data-source', window.location.href)

  if $('#dataset_payload_type').val() == 'data'
    external_prepare_table_for_cubification()
    $('#cubify_form')
      .attr(
        'action',
        '/query/save_data?redirect=' + $('#dataset_redirect').val()
      )
      .submit()
  else if $('#dataset_payload_type').val() == 'query'
    $('#cubify_form')
      .attr('action', '/query/save_query')
      .submit()



###
Helper Functions
###

abort_all_ajax_calls = () ->
  # Clear the ajaxQueue
  debug 'Clearing the ajaxQueue'
  $.ajaxQueue.clear()

  # Abort all currently active AJAX calls
  if $('body').data('xhrPool').length > 0
    debug "Aborting #{$('body').data('xhrPool').length} AJAX call(s)"
    $.each(
      $('body').data('xhrPool'),
      (index, jqXHR) ->
        if jqXHR
          jqXHR.abort()
    )
    $('body').data('xhrPool').length = 0


add_batch_of_cells_to_results_table = (subjects, predicate) ->
  deferred = $.Deferred()

  batch_subject = subjects[0].replace(/(http)s?\:\/\//g, '').replace(
    /[^a-zA-Z0-9]/g, '_'
  )
  batch_predicate = predicate['uri'].replace(/(http)s?\:\/\//g, '').replace(
    /[^a-zA-Z0-9]/g, '_'
  )
  time = new Date().getTime()
  batch_id = "batch_#{time}__#{batch_predicate}__#{batch_subject}"

  for subject in subjects
    $("#results tr[data-s=\"#{subject}\"]").append(
      """
      <td class="#{batch_id}" data-s="#{subject}" data-p="#{predicate['uri']}"
      data-inverse="#{predicate['inverse']}"></td>
      """
    )

  Spinners
    .create(
      ".#{batch_id}",
      {
        radius: 3,
        dashes: 10,
        width: 1,
        height: 3,
        opacity: 1,
        padding: 0,
        rotation: 600,
        color: '#000000'
      }
    )
    .play()

  $.when(
    get_the_objects(subjects, predicate)
  )
  .done(
    (data) ->
      # SPARQL performance
      log_sparql_query_runtime(
        data['runtime'],
        'for getting the objects',
        data['query'],
      )

      Spinners.get(".#{batch_id}").remove()

      if data['objects'].length > 0
        guess_and_set_column_types(data)

        if are_we_in_dataset_mode()
          set_cube_column_types(data)

        prepare_data_and_add_to_cells(data)

        deferred.resolve(
          """Added #{data['objects'].length} objects for #{predicate['uri']},
          inverse #{predicate['inverse']}"""
        )

      else
        deferred.resolve(
          """Received no objects for #{predicate['uri']},
          inverse #{predicate['inverse']}"""
        )
  )

  return deferred.promise()


add_cells_to_results_table = (subjects, predicate) ->
  deferred = $.Deferred()

  copied_subjects = subjects[..]

  batch_counter = 0
  batch_count = Math.ceil(subjects.length / $('body').data('BATCH_SIZE'))

  while copied_subjects.length > 0
    if copied_subjects.length > $('body').data('BATCH_SIZE')
      # Mind the 3 dots!
      sliced_subjects = copied_subjects[...$('body').data('BATCH_SIZE')]
      # Mind the 2 dots!
      copied_subjects = copied_subjects[$('body').data('BATCH_SIZE')..]
    else
      # Mind the 2 dots!
      sliced_subjects = copied_subjects[..]
      copied_subjects.length = 0

    $.when(
      add_batch_of_cells_to_results_table(sliced_subjects, predicate)
    )
    .done(
      (data) ->
        debug data

        batch_counter += 1
        if batch_counter is batch_count
          deferred.resolve(
            "Finished #{batch_counter} batch(es) of getting objects"
          )
    )

  return deferred.promise()


add_column_for_given_predicate = (predicate) ->
  deferred = $.Deferred()

  # Make sure the inverse attribute is set
  if not predicate['inverse']
    predicate['inverse'] = false

  available_predicate = \
    $("""#available_predicates a[data-uri="#{predicate['uri']}"][data-inverse="#{predicate['inverse']}"]""")

  # Get the label
  label = available_predicate.attr('data-label')
  if not label
    label = shorten_uri(predicate['uri'])

  # Remove entry for predicate from list of available predicates
  available_predicate.parent().remove()

  # Add the predicate to the data structure
  if not is_predicate_already_in_data_structure(predicate)
    $('body')
      .data('predicates')
      .push({
        'uri': predicate['uri'],
        'inverse': predicate['inverse'],
      })

  # If the table has no rows, add some
  if $('#results tr').length is 0
    # Add one for the header
    $('#results').append('<tr></tr>')
    # Add one for each subject
    for subject in $('body').data('subjects')
      $('#results').append("<tr data-s=\"#{subject}\"></tr>")

  # Add table header
  th = $("""
    <th data-label="#{label}" data-uri="#{predicate['uri']}"
    data-inverse="#{predicate['inverse']}" title="#{predicate['uri']}">
      <div class="btn-group navbar-left title">
        <button type="button" class="btn btn-primary btn-sm dropdown-toggle"
        data-toggle="dropdown" href="#">
          #{label} <span class="caret"></span>
        </button>
        <ul class="dropdown-menu" style="text-align: left;"></ul>
      </div>
      <div class="btn-group navbar-left filter">
      </div>
    </th>
  """)
  $('#results tr:first').append(th)

  # Add the option to remove the column
  th.find("ul").first()
    .append(
      """
      <li>
        <a class="remove_predicate" href="#">
          <span class="glyphicon glyphicon-trash"></span> Remove column
        </a>
      </li>
      """
    )

  # Column has an active search filter
  search_term = get_search_filter_for_predicate(predicate)
  if search_term
    th.find('.filter').html(
      """
        <div class="dropdown">
          <button type="button" class="btn btn-default btn-xs dropdown-toggle"
          data-toggle="dropdown">
            <span class="glyphicon glyphicon-filter"></span>
            "#{search_term}" <span class="caret"></span>
          </button>
          <ul class="dropdown-menu">
            <li>
              <a href="#" class="edit_search_filter">
                <span class="glyphicon glyphicon-pencil"></span>
                Edit filter &hellip;
              </a>
            </li>
            <li>
              <a href="#" class="remove_filter">
                <span class="glyphicon glyphicon-remove"></span>
                Remove filter
              </a>
            </li>
          </ul>
        </div>
      """
    )

  # Column has an active URI filter
  uri_filter = get_uri_filter_for_predicate(predicate)
  if uri_filter
    if not uri_filter['label']
      uri_filter['label'] = shorten_uri(uri_filter['value'])

    th.find('.filter').html(
      """
        <div class="dropdown">
          <button type="button" class="btn btn-default btn-xs dropdown-toggle"
          data-toggle="dropdown">
            <span class="glyphicon glyphicon-filter"></span>
            #{uri_filter['label']} <span class="caret"></span>
          </button>
          <ul class="dropdown-menu">
            <li>
              <a href="#" class="remove_filter">
                <span class="glyphicon glyphicon-remove"></span> Remove filter
              </a>
            </li>
          </ul>
        </div>
      """
    )

  # Column has an active date filter
  date_filter = get_date_filter_for_predicate(predicate)
  if date_filter
    th.find('.filter').html(
      """
        <div class="dropdown">
          <button type="button" class="btn btn-default btn-xs dropdown-toggle"
            data-toggle="dropdown">
            <span class="glyphicon glyphicon-filter"></span>
            #{date_filter['label']} <span class="caret"></span>
          </button>
          <ul class="dropdown-menu">
            <li>
              <a href="#" class="edit_date_filter">
                <span class="glyphicon glyphicon-pencil"></span>
                Edit filter &hellip;
              </a>
            </li>
            <li>
              <a href="#" class="remove_filter">
                <span class="glyphicon glyphicon-remove"></span>
                Remove filter
              </a>
            </li>
          </ul>
        </div>
      """
    )

  # Column has an active datetime filter
  datetime_filter = get_datetime_filter_for_predicate(predicate)
  if datetime_filter
    th.find('.filter').html(
      """
        <div class="dropdown">
          <button type="button" class="btn btn-default btn-xs dropdown-toggle"
          data-toggle="dropdown">
            <span class="glyphicon glyphicon-filter"></span>
            #{datetime_filter['label']} <span class="caret"></span>
          </button>
          <ul class="dropdown-menu">
            <li>
              <a href="#" class="edit_datetime_filter">
                <span class="glyphicon glyphicon-pencil"></span>
                Edit filter &hellip;
              </a>
            </li>
            <li>
              <a href="#" class="remove_filter">
                <span class="glyphicon glyphicon-remove"></span>
                Remove filter
              </a>
            </li>
          </ul>
        </div>
      """
    )

  # Column has an active numeric filter
  numeric_filter = get_numeric_filter_for_predicate(predicate)
  if numeric_filter
    th.find('.filter').html(
      """
        <div class="dropdown">
          <button type="button" class="btn btn-default btn-xs dropdown-toggle"
          data-toggle="dropdown">
            <span class="glyphicon glyphicon-filter"></span>
            #{numeric_filter['label']} <span class="caret"></span>
          </button>
          <ul class="dropdown-menu">
            <li>
              <a href="#" class="edit_numeric_filter">
                <span class="glyphicon glyphicon-pencil"></span>
                Edit filter &hellip;
              </a>
            </li>
            <li>
              <a href="#" class="remove_filter">
                <span class="glyphicon glyphicon-remove"></span>
                Remove filter
              </a>
            </li>
          </ul>
        </div>
      """
    )

  # Column has an active "not empty filter"
  not_empty_filter = get_not_empty_filter_for_predicate(predicate)
  if not_empty_filter
    th.find('.filter').html("""
    <div class="dropdown">
      <button type="button" class="btn btn-default btn-xs dropdown-toggle"
      data-toggle="dropdown">
        <span class="glyphicon glyphicon-filter"></span>
        Hide empty results <span class="caret"></span>
      </button>
      <ul class="dropdown-menu">
        <li>
          <a href="#" class="remove_filter">
            <span class="glyphicon glyphicon-remove"></span> Remove filter
          </a>
        </li>
      </ul>
    </div>
    """)

  # If no filter is active, provide the "not empty filter" menu item
  if (not search_term and
      not uri_filter and
      not date_filter and
      not datetime_filter and
      not numeric_filter and
      not not_empty_filter)
    th.find('.title ul').prepend(
      """
        <li class="not_empty_filter">
          <a href="#" class="add_not_empty_filter">
            <span class="glyphicon glyphicon-filter"></span> Hide empty results
          </a>
        </li>
      """
    )

  $.when(
    add_cells_to_results_table($('body').data('subjects'), predicate)
  )
  .done(
    (data) ->
      debug data

      deferred.resolve("Added column for #{predicate['uri']}")
  )

  return deferred.promise()


add_columns = () ->
  deferred = $.Deferred()

  if $('body').data('predicates').length > 0
    $.when(
      add_columns_based_on_data_structure()
    )
    .done(
      (data) ->
        debug data
        deferred.resolve('Added all columns')
    )

  else if are_we_in_dataset_mode()
    $.when(
      add_columns_based_on_dimensions_and_measures()
    )
    .done(
      (data) ->
        debug data
        deferred.resolve('Added all columns')
    )

  else
    deferred.resolve('ERROR: This should never happen.')

  return deferred.promise()


add_columns_based_on_data_structure = () ->
  deferred = $.Deferred()

  added_columns_counter = 0

  for predicate in $('body').data('predicates')
    $.when(
      add_column_for_given_predicate(predicate)
    )
    .done(
      (data) ->
        debug data

        added_columns_counter += 1
        if added_columns_counter is $('body').data('predicates').length
          deferred.resolve('Added all columns based on data structure')
    )

  return deferred.promise()


add_columns_based_on_dimensions_and_measures = () ->
  deferred = $.Deferred()

  $.when(
    add_columns_for_all_dimensions(),
    add_columns_for_all_measures()
  )
  .done(
    (dimension_data, measure_data) ->
      debug dimension_data
      debug measure_data

      # Update the address, but not the history
      $.address.history(false)
      update_the_address()
      $.address.history(true)

      if (Object.keys($('body').data('dimensions')).length is 0 and
          Object.keys($('body').data('measures')).length is 0)
        debug 'No dimensions or measures found!'
        ui_display_results_page_alert(
          """It looks as if this dataset has
          <strong>no defined dimensions or measures!</strong>"""
        )

      else if Object.keys($('body').data('dimensions')).length is 0
        debug 'No dimensions found!'
        ui_display_results_page_alert(
          """It looks as if this dataset has
          <strong>no defined dimensions!</strong>"""
        )

      else if Object.keys($('body').data('measures')).length is 0
        debug 'No measures found!'
        ui_display_results_page_alert(
          """It looks as if this dataset has
          <strong>no defined measures!</strong>"""
        )

      deferred.resolve('Added columns for dimensions and measures')
  )

  return deferred.promise()


add_columns_for_all_dimensions = () ->
  deferred = $.Deferred()

  if Object.keys($('body').data('dimensions')).length is 0
    deferred.resolve("There are no dimensions to add")
  else
    added_columns_counter = 0

    dimension_list = []
    for dimension_uri, dimension of $('body').data('dimensions')
      dimension_list.push({
        uri: dimension_uri,
        label: dimension['label']
      })

    dimension_list = dimension_list.sort(
      (a, b) ->
        if (a.label.toLowerCase() > b.label.toLowerCase())
          return 1
        if (a.label.toLowerCase() < b.label.toLowerCase())
          return -1
        # a is equal to b
        return 0
    )

    for dimension in dimension_list
      $.when(
        add_column_for_given_predicate(dimension)
      )
      .done(
        (data) ->
          debug data

          added_columns_counter += 1
          if added_columns_counter is \
              Object.keys($('body').data('dimensions')).length
            deferred.resolve("Added #{added_columns_counter} dimension columns")
      )

  return deferred.promise()


add_columns_for_all_measures = () ->
  deferred = $.Deferred()

  if Object.keys($('body').data('measures')).length is 0
    deferred.resolve("There are no measures to add")
  else
    added_columns_counter = 0

    measure_list = []
    for measure_uri, measure of $('body').data('measures')
      measure_list.push({
        uri: measure_uri,
        label: measure['label']
      })

    measure_list = measure_list.sort(
      (a, b) ->
        if (a.label.toLowerCase() > b.label.toLowerCase())
          return 1
        if (a.label.toLowerCase() < b.label.toLowerCase())
          return -1
        # a is equal to b
        return 0
    )

    for measure in measure_list
      $.when(
        add_column_for_given_predicate(measure)
      )
      .done(
        (data) ->
          debug data

          added_columns_counter += 1
          if added_columns_counter is \
              Object.keys($('body').data('measures')).length
            deferred.resolve("Added #{added_columns_counter} measure columns")
      )

  return deferred.promise()


are_we_in_dataset_mode = () ->
  if $('body').data('dataset')
    return true
  else
    return false


clear_results = () ->
  $('body').data('subjects', [])
  $("#results tr:not(:first)").remove()
  $('div#load_more').html('')
  $('#results_count').hide()
  $('body').data('total_results_count', 0)
  $('ul#available_predicates').empty()


count_filters = () ->
  count = 0
  for candidate in $('body').data('predicates')
    count += 1 if candidate['filter_type']
  return count


debug = (data) ->
  if $('body').data('DEBUG')
    console.log data


get_additional_subjects = (load_size) ->
  deferred = $.Deferred()

  ui_display_spinner()
  $('#add_column').hide()

  $.when(
    get_batch_of_additional_subjects()
  )
  .done(
    (data) ->
      debug data

      ui_clear_spinner()

      if load_size > 10
        get_additional_subjects(load_size - $('body').data('BATCH_SIZE'))
      else
        ui_update_the_load_more_results_area(load_size)
        $('#navbar_container').show()
        $('#add_column').css('display', 'inline-block')
        $('#results_count').show()

        deferred.resolve("Finished getting additional subjects")
  )

  return deferred.promise()


get_and_add_predicates_used_by_subjects = (subjects) ->
  deferred = $.Deferred()

  $.ajax({
    url: '/query/get_predicates_used_by_subjects',
    type: 'POST',
    data: JSON.stringify({
      endpoint_url: $('body').data('endpoint'),
      search_type: $('body').data('search_type'),
      subjects: subjects
    })
  })
  .done(
    (predicates_data) ->
      # SPARQL performance
      log_sparql_query_runtime(
        predicates_data['runtime'],
        'for getting the available predicates',
        predicates_data['query'],
      )

      # Add the available predicates to the list
      for predicate in predicates_data.predicates
        # Check if this predicate has already been added
        # to the list of available predicates before
        if ($("""#available_predicates a[data-uri="#{predicate.uri}"][data-inverse="#{predicate.inverse}"]""").length is 0 and
            not is_predicate_already_displayed(predicate))
          debug("Added '#{predicate.label}' (#{predicate.uri})" +
            " to the list of available predicates")
          # Mark DBpedia 'property' predicates as old
          label_suffix = ''
          if predicate.uri.indexOf('http://dbpedia.org/property/') >= 0
            label_suffix = ' (old)'
          # Add the predicate to the list
          $('#available_predicates').append(
            """
            <li>
              <a
                class="add_predicate"
                data-label="#{predicate.label}#{label_suffix}"
                data-uri="#{predicate.uri}"
                data-inverse="#{predicate.inverse}"
                title="#{predicate.uri}"
                href="#">#{predicate.label}#{label_suffix}</a>
            </li>
            """
          )

      # Sort the list of available predicates
      listitems = $('#available_predicates').children('li').get().sort(
        (a, b) ->
          $(a).text().toUpperCase().localeCompare(
            $(b).text().toUpperCase()
          )
      )
      for item in listitems
        $('#available_predicates').append(item)

      deferred.resolve("Processed #{listitems.length} predicates")
  )

  return deferred.promise()


get_and_display_the_dataset_label = () ->
  deferred = $.Deferred()

  if not are_we_in_dataset_mode()
    deferred.resolve("We're not in dataset mode, nothing to do here")

  else
    $.ajax({
      url: '/query/get_dataset_label',
      type: 'POST',
      data: JSON.stringify({
        dataset_uri: $('body').data('dataset'),
        endpoint_url: $('body').data('endpoint'),
        search_type: $('body').data('search_type'),
      })
    })
    .done(
      (data) ->
        description = data['dataset']['description']
        if not description
          description = 'No description available'

        $('#dataset_title .panel-body').html(
          """
          <strong><span id='dataset_label'>
            #{data['dataset']['label']}
          </span></strong><br />
          <span id='dataset_description'>#{description}</span><br />
          (Source: <a href="#{data['endpoint']['website_url']}"
          target="_blank">#{data['endpoint']['label']}</a>)
          """
        )
        $('#dataset_title').show()

        deferred.resolve("Displayed the dataset label")
    )

  return deferred.promise()


get_and_display_the_datasets_of_the_selected_endpoint = () ->
  # Make sure the right endpoint is selected in the dropdown list
  ep = $('body').data('endpoint')
  $("#dataset_endpoint_selector>option[value='#{ep}']").prop('selected', true)

  # Also change the search endpoint selector, if the endpoint URL parameter is set
  if 'endpoint' in $.address.parameterNames()
    $("#ep>option[value='#{ep}']").prop('selected', true)

  # Empty the list of datasets
  $('#dataset_list').empty()

  # Add a "loading, please wait" message
  $('#endpoint_title').html('Loading datasets, please wait …')
  $('#endpoint_datasets_count').html('0 datasets')

  $('#endpoint_description').html('')
  Spinners
    .create(
      '#endpoint_description',
      {
        radius: 5,
        dashes: 12,
        width: 2,
        height: 5,
        opacity: 1,
        padding: 0,
        rotation: 600,
        color: '#000000'
      }
    )
    .play()

  # Get the datasets
  $.ajax({
    url: '/query/get_datasets',
    type: 'POST',
    data: JSON.stringify({
      endpoint_url: $('body').data('endpoint'),
      search_type: $('body').data('search_type'),
    })
  })
  .done(
    (data) ->
      # Update the endpoint metadata
      $('#endpoint_title').html(data.endpoint.label)
      $('#endpoint_description').html(
        'More info at <a href="' +
        data.endpoint.website_url +
        '" target="_blank">' +
        data.endpoint.website_url +
        '</a>'
      )
      $('#endpoint_datasets_count').html(data.datasets.length + ' datasets')

      # Update the datasets
      for dataset in data.datasets
        dataset_size = ''
        if dataset.size > 0
          dataset_size = " (#{dataset.size} entries)"
        datasetUri = encodeURIComponent(dataset.uri)
        url = "#?dataset=#{datasetUri}&amp;"
        url += "endpoint=#{encodeURIComponent($('body').data('endpoint'))}"
        dataset_li = """
        <li class="list-group-item">
          <input type="checkbox" title="Compare in Vis Wizard" class="compare" data-dataset="#{datasetUri}" />
          <span class="pull-right" style="padding:0 0 10px 10px;">
            <a href="/vis#{url}">
              <img src="/static/img/cubevis.png"
              title="Visualize the data" class="cubevis"
              onmouseover="$(this).tooltip('show')">
            </a>
          </span>
          <a href="/search#{url}"
          title="Display the data#{dataset_size}"
          onmouseover="$(this).tooltip('show')">#{dataset.label}</a>
        </li>
        """
        $('#dataset_list').append(dataset_li)

      # Spinner cleanup
      Spinners.removeDetached()
  )


get_and_save_cube_dimensions_and_measures = () ->
  deferred = $.Deferred()

  if not are_we_in_dataset_mode()
    deferred.resolve(
      "We're not in dataset mode"
    )

  else
    $.ajax({
      url: '/query/get_cube_dimensions_and_measures',
      type: 'POST',
      data: JSON.stringify({
        endpoint_url: $('body').data('endpoint'),
        search_type: $('body').data('search_type'),
        dataset: $('body').data('dataset'),
      })
    })
    .done(
      (data) ->
        if data['dimensions'].length < 2
          $('#menu_aggregate_dataset').hide()
        else
          $('#menu_aggregate_dataset').show()

        # Save the lists of dimensions
        dimensions = {}
        for dimension in data['dimensions']
          dimensions[dimension['uri']] = {'label': dimension['label']}
        $('body').data('dimensions', dimensions)

        # Save the lists of measures
        measures = {}
        for measure in data['measures']
          measures[measure['uri']] = {'label': measure['label']}
        $('body').data('measures', measures)

        deferred.resolve(
          "Received #{data['dimensions'].length} dimension(s) and " +
          "#{data['measures'].length} measure(s)"
        )
    )

  return deferred.promise()


get_batch_of_additional_subjects = () ->
  deferred = $.Deferred()

  $.when(
    get_the_subjects()
  )
  .done(
    (subjects_data) ->
      # SPARQL performance
      log_sparql_query_runtime(
        subjects_data['runtime'],
        'for getting the subjects',
        subjects_data['query'],
      )

      # We received no subjects
      if subjects_data.subjects.length is 0
        ui_clear_spinner()
        $('div#load_more').html('')
        deferred.resolve('We are done! =)')
        return

      ui_clear_spinner()

      # Save the result URIs as data to the results table
      for subject in subjects_data.subjects
        $('body').data('subjects').push(subject)

      $.when(
        get_and_add_predicates_used_by_subjects(subjects_data.subjects)
      )
      .done(
        (data) ->
          debug data

          # Add new rows
          for subject in subjects_data.subjects
            $('#results').append("<tr data-s=\"#{subject}\"></tr>")

          ui_update_the_results_count()

          # Get the objects for the new subjects and all predicates
          get_objects_counter = 0

          for predicate in $('body').data('predicates')
            $.when(
              add_cells_to_results_table(
                subjects_data.subjects,
                {
                  'uri': predicate['uri'],
                  'inverse': predicate['inverse'],
                },
              )
            )
            .done(
              (data) ->
                debug data

                get_objects_counter += 1
                if get_objects_counter is $('body').data('predicates').length
                  deferred.resolve('We are done! =)')
            )
      )
  )

  return deferred.promise()


get_search_filter_for_predicate = (predicate) ->
  # Iterate through all displayed predicates
  for candidate in $('body').data('predicates')
    if (candidate['uri'] == predicate['uri'] and
        candidate['filter_type'] == 'search')
      return candidate['filter_value']

  # No matching filter
  return false


get_the_objects = (subjects, predicate) ->
  return $.ajaxQueue({
    url: '/query/get_objects_for_predicate',
    type: 'POST',
    data: JSON.stringify({
      endpoint_url: $('body').data('endpoint'),
      search_type: $('body').data('search_type'),
      subjects: subjects,
      predicate: predicate,
    })
  })


get_the_subjects = () ->
  return $.ajaxQueue({
    url: '/query/get_subjects',
    type: 'POST',
    data: JSON.stringify({
      endpoint_url: $('body').data('endpoint'),
      search_type: $('body').data('search_type'),
      predicates: $('body').data('predicates'),
      offset: $('body').data('subjects').length,
      dataset: $('body').data('dataset'),
    })
  })


get_not_empty_filter_for_predicate = (predicate) ->
  # Iterate through all displayed predicates
  for candidate in $('body').data('predicates')
    if (candidate['uri'] is predicate['uri'] and
        candidate['inverse'] is predicate['inverse'] and
        candidate['filter_type'] is 'not_empty')
      return true

  # No matching filter
  return false


get_date_filter_for_predicate = (predicate) ->
  # Iterate through all displayed predicates
  for candidate in $('body').data('predicates')
    if (candidate['uri'] is predicate['uri'] and
        candidate['inverse'] is predicate['inverse'] and
        candidate['filter_type'] is 'date')
      min = candidate['filter_value'].split(',')[0]
      max = candidate['filter_value'].split(',')[1]

      response = {}
      response['value'] = candidate['filter_value']

      if min and max
        response['label'] = "#{min}–#{max}"
      else if min
        response['label'] = "&ge; #{min}"
      else if max
        response['label'] = "&le; #{max}"

      return response

  # No matching filter
  return false


get_datetime_filter_for_predicate = (predicate) ->
  # Iterate through all displayed predicates
  for candidate in $('body').data('predicates')
    if (candidate['uri'] is predicate['uri'] and
        candidate['inverse'] is predicate['inverse'] and
        candidate['filter_type'] is 'datetime')
      min = candidate['filter_value'].split(',')[0]
      max = candidate['filter_value'].split(',')[1]

      response = {}
      response['value'] = candidate['filter_value']

      if min and max
        response['label'] = "#{min}–#{max}"
      else if min
        response['label'] = "&ge; #{min}"
      else if max
        response['label'] = "&le; #{max}"

      return response

  # No matching filter
  return false


get_numeric_filter_for_predicate = (predicate) ->
  # Iterate through all displayed predicates
  for candidate in $('body').data('predicates')
    if (candidate['uri'] is predicate['uri'] and
        candidate['inverse'] is predicate['inverse'] and
        candidate['filter_type'] is 'numeric')
      min = candidate['filter_value'].split(',')[0]
      max = candidate['filter_value'].split(',')[1]

      response = {}
      response['value'] = candidate['filter_value']

      if min and max
        response['label'] = "#{min}–#{max}"
      else if min
        response['label'] = "&ge; #{min}"
      else if max
        response['label'] = "&le; #{max}"

      return response

  # No matching filter
  return false


get_uri_filter_for_predicate = (predicate) ->
  # Iterate through all displayed predicates
  for candidate in $('body').data('predicates')
    if (candidate['uri'] is predicate['uri'] and
        candidate['inverse'] is predicate['inverse'] and
        candidate['filter_type'] is 'uri')
      response = {}
      response['value'] = candidate['filter_value']
      if candidate['filter_label']
        response['label'] = candidate['filter_label']

      return response

  # No matching filter
  return false


guess_and_set_column_types = (data) ->
  th = $("""th[data-uri="#{data['predicate']['uri']}"][data-inverse="#{data['predicate']['inverse']}"]""")
  td = $("""td[data-p="#{data['predicate']['uri']}"][data-inverse="#{data['predicate']['inverse']}"]""")
  datatype = data['objects'][0]['o']['datatype']

  # Get the index for the current column (predicate)
  p_index = th.prevAll("th").length

  if not $('body').data('predicates')[p_index]
    debug 'ERROR: Trying to find the predicate in the table. Failing.'
    return

  # Hypothesis 0: If we received multiple values for a cell,
  # let's ignore the column for now
  multivalue_column_detector = {}
  for object in data['objects']
    if not multivalue_column_detector[object['s']]
      multivalue_column_detector[object['s']] = 1
    else
      if not are_we_in_dataset_mode()
        $('body').data('predicates')[p_index]['cube_component_type'] = \
          'multivalue'
        break

  if $('body').data('predicates')[p_index]['cube_component_type'] == \
      'multivalue'
    th.find("li.column_type").remove()
    th.find("ul").first()
      .append(
        """
        <li style="font-weight: normal;" class="column_type">
          <a class="cube_info guessed_multivalue" href="#">
            <span class="glyphicon glyphicon-info-sign"></span>
            This is probably a multi-value column.
          </a>
        </li>
        """
      )

    if not are_we_in_dataset_mode()
      th.attr('data-component', 'multivalue')
      td.attr('data-component', 'multivalue')
        .addClass('multivalue')
        .removeClass('dimension')
        .removeClass('measure')

  # Special case: If the predicate is 'http://data.lod2.eu/scoreboard/properties/value',
  # it's always a measure
  # FIXME: Code duplications
  else if data['predicate']['uri'] == 'http://data.lod2.eu/scoreboard/properties/value'
    if not are_we_in_dataset_mode()
      $('body').data('predicates')[p_index]['cube_component_type'] = 'measure'

    # Add the option to set a numeric filter if the datatype is numeric
    if (datatype == 'http://www.w3.org/2001/XMLSchema#integer' or
        datatype == 'http://www.w3.org/2001/XMLSchema#decimal' or
        datatype == 'http://www.w3.org/2001/XMLSchema#float' or
        datatype == 'http://www.w3.org/2001/XMLSchema#double' or
        datatype == 'http://www.w3.org/2001/XMLSchema#nonPositiveInteger' or
        datatype == 'http://www.w3.org/2001/XMLSchema#negativeInteger' or
        datatype == 'http://www.w3.org/2001/XMLSchema#long' or
        datatype == 'http://www.w3.org/2001/XMLSchema#int' or
        datatype == 'http://www.w3.org/2001/XMLSchema#short' or
        datatype == 'http://www.w3.org/2001/XMLSchema#byte' or
        datatype == 'http://www.w3.org/2001/XMLSchema#nonNegativeInteger' or
        datatype == 'http://www.w3.org/2001/XMLSchema#unsignedLong' or
        datatype == 'http://www.w3.org/2001/XMLSchema#unsignedInt' or
        datatype == 'http://www.w3.org/2001/XMLSchema#unsignedShort' or
        datatype == 'http://www.w3.org/2001/XMLSchema#unsignedByte' or
        datatype == 'http://www.w3.org/2001/XMLSchema#positiveInteger')
      th.find(".numeric_filter").remove()
      th.find("ul").first()
        .prepend(
          """
          <li class="numeric_filter">
            <a href="#" class="add_numeric_filter">
              <span class="glyphicon glyphicon-filter"></span>
              Add filter &hellip;
            </a>
          </li>
          """
        )
      if $('body').data('predicates')[p_index]['filter_type'] == 'numeric'
        th.find('.numeric_filter').hide()

    else
      debug(
        "Didn't add a filter, datatype was " +
        data['objects'][0]['o']['datatype']
      )


    th.find(".column_type").remove()
    th.find("ul").first()
      .append(
        """
        <li class="column_type measure" style="font-weight: normal;">
          <a class="cube_info guessed_measure" href="#">
            <span class="glyphicon glyphicon-info-sign"></span>
            This is probably a cube measure.
          </a>
        </li>
        """
      )

    if not are_we_in_dataset_mode()
      th.attr('data-component', 'observation')
      td.attr('data-component', 'observation')
        .attr(
          'data-range', 'http://code-research.eu/resource#CubeObservationNumber'
        )
        .addClass('measure')
        .removeClass('dimension')


  # Hypothesis 1: If it's not a typed literal,
  # or it is an xsd:date or xsd:dateTime, it's probably a dimension
  else if data['objects'][0]['o']['type'] != 'typed-literal' or
          datatype == 'http://www.w3.org/2001/XMLSchema#date' or
          datatype == 'http://www.w3.org/2001/XMLSchema#dateTime'
    if not are_we_in_dataset_mode()
      $('body').data('predicates')[p_index]['cube_component_type'] = 'dimension'

    th.find("li.column_type").remove()
    th.find("ul").first()
      .append(
        """
        <li class="column_type dimension" style="font-weight: normal;">
          <a class="cube_info guessed_dimension" href="#">
            <span class="glyphicon glyphicon-info-sign"></span>
            This is probably a cube dimension.
          </a>
        </li>
        """
      )

    if not are_we_in_dataset_mode()
      th.attr('data-component', 'dimension')
      td.attr('data-component', 'dimension')
        .attr(
          'data-range', 'http://code-research.eu/resource#CubeDimensionNominal'
        )
        .addClass('dimension')
        .removeClass('measure')

    # Add a search filter menu entry
    if data['objects'][0]['o']['type'] == 'literal'
      th.find(".search_filter").remove()
      th.find("ul").first()
        .prepend(
          """
          <li class="search_filter">
            <a href="#" class="add_search_filter">
              <span class="glyphicon glyphicon-filter"></span>
              Add filter &hellip;
            </a>
          </li>
          """
        )
      if $('body').data('predicates')[p_index]['filter_type'] == 'search'
        th.find('.search_filter').hide()

    # Add a date filter menu entry
    if datatype == 'http://www.w3.org/2001/XMLSchema#date'
      th.find(".date_filter").remove()
      th.find("ul").first()
        .prepend(
          """
          <li class="date_filter">
            <a href="#" class="add_date_filter">
              <span class="glyphicon glyphicon-filter"></span>
              Add filter &hellip;
            </a>
          </li>
          """
        )
      if $('body').data('predicates')[p_index]['filter_type'] == 'date'
        th.find('.date_filter').hide()

    # Add a datetime filter menu entry
    if datatype == 'http://www.w3.org/2001/XMLSchema#dateTime'
      th.find(".datetime_filter").remove()
      th.find("ul").first()
        .prepend(
          """
          <li class="datetime_filter">
            <a href="#" class="add_datetime_filter">
              <span class="glyphicon glyphicon-filter"></span>
              Add filter &hellip;
            </a>
          </li>
          """
        )
      if $('body').data('predicates')[p_index]['filter_type'] == 'datetime'
        th.find('.datetime_filter').hide()


  # Hypothesis 2: If it's a typed literal, it's probably a measure
  else
    if not are_we_in_dataset_mode()
      $('body').data('predicates')[p_index]['cube_component_type'] = 'measure'

    # Add the option to set a numeric filter if the datatype is numeric
    if (datatype == 'http://www.w3.org/2001/XMLSchema#integer' or
        datatype == 'http://www.w3.org/2001/XMLSchema#decimal' or
        datatype == 'http://www.w3.org/2001/XMLSchema#float' or
        datatype == 'http://www.w3.org/2001/XMLSchema#double' or
        datatype == 'http://www.w3.org/2001/XMLSchema#nonPositiveInteger' or
        datatype == 'http://www.w3.org/2001/XMLSchema#negativeInteger' or
        datatype == 'http://www.w3.org/2001/XMLSchema#long' or
        datatype == 'http://www.w3.org/2001/XMLSchema#int' or
        datatype == 'http://www.w3.org/2001/XMLSchema#short' or
        datatype == 'http://www.w3.org/2001/XMLSchema#byte' or
        datatype == 'http://www.w3.org/2001/XMLSchema#nonNegativeInteger' or
        datatype == 'http://www.w3.org/2001/XMLSchema#unsignedLong' or
        datatype == 'http://www.w3.org/2001/XMLSchema#unsignedInt' or
        datatype == 'http://www.w3.org/2001/XMLSchema#unsignedShort' or
        datatype == 'http://www.w3.org/2001/XMLSchema#unsignedByte' or
        datatype == 'http://www.w3.org/2001/XMLSchema#positiveInteger')
      th.find(".numeric_filter").remove()
      th.find("ul").first()
        .prepend(
          """
          <li class="numeric_filter">
            <a href="#" class="add_numeric_filter">
              <span class="glyphicon glyphicon-filter"></span>
              Add filter &hellip;
            </a>
          </li>
          """
        )
      if $('body').data('predicates')[p_index]['filter_type'] == 'numeric'
        th.find('.numeric_filter').hide()

    else
      debug(
        "Didn't add a filter, datatype was " +
        data['objects'][0]['o']['datatype']
      )


    th.find(".column_type").remove()
    th.find("ul").first()
      .append(
        """
        <li class="column_type measure" style="font-weight: normal;">
          <a class="cube_info guessed_measure" href="#">
            <span class="glyphicon glyphicon-info-sign"></span>
            This is probably a cube measure.
          </a>
        </li>
        """
      )

    if not are_we_in_dataset_mode()
      th.attr('data-component', 'observation')
      td.attr('data-component', 'observation')
        .attr(
          'data-range', 'http://code-research.eu/resource#CubeObservationNumber'
        )
        .addClass('measure')
        .removeClass('dimension')


initial_search = () ->
  deferred = $.Deferred()

  ui_display_the_results_page()
  ui_display_spinner()

  # Clear the SPARQL log
  $('#sparql_log').empty()

  # Get the subjects
  get_subjects_request = get_the_subjects()

  # Display a message if the request is still pending after 2 seconds
  slow_endpoint_alert = ->
    if get_subjects_request.state() == 'pending'
      ui_display_results_page_alert("""
      The SPARQL endpoint <em>#{$('body').data('endpoint')}</em> is taking a
      long time to respond. Sorry about that!<br/>
      If you'd like, you can take a look at the
      <a data-toggle="modal" href="#sparql_runtime_modal">SPARQL Query Log</a>
      """)
  window.setTimeout(slow_endpoint_alert, 3000)

  $.when(
    get_subjects_request,
    get_and_save_cube_dimensions_and_measures()
  )
  .done(
    (subjects_data, dimensions_and_measures_data) ->
      subjects_data = subjects_data[0]
      debug dimensions_and_measures_data

      # SPARQL performance
      log_sparql_query_runtime(
        subjects_data['runtime'],
        'for getting the subjects',
        subjects_data['query'],
      )

      # Save the SPARQL endpoint URL
      $('body').data('endpoint', subjects_data['endpoint_url'])

      # We received no subjects
      if subjects_data.subjects.length is 0
        ui_clear_spinner()
        ui_display_the_front_page()
        ui_display_front_page_alert(
          """<strong>Nothing found!</strong>
          Please try again with another search."""
        )
        return

      for subject in subjects_data.subjects
        $('body').data('subjects').push(subject)

      $.when(
        get_and_add_predicates_used_by_subjects(subjects_data.subjects),
        get_and_display_the_dataset_label()
      )
      .done(
        (predicates_data, dataset_data) ->
          debug predicates_data
          debug dataset_data

          ui_clear_spinner()
          $.when(
            ui_get_and_display_the_total_results_count()
          )
          .done(
            (data) ->
              debug data

              ui_update_the_load_more_results_area(
                subjects_data.subjects.length
              )
          )

          ui_update_the_results_count()
          $('#navbar_container').show()
          $('#add_column').css('display', 'inline-block')

          $.when(
            add_columns()
          )
          .done(
            (data) ->
              debug data

              update_the_address()

              deferred.resolve('We are done! =)')
          )
      )
  )

  return deferred.promise()


is_predicate_already_displayed = (predicate) ->
  # Iterate through all displayed predicates
  displayed = false
  $('#results th').each(
    () ->
      if ($(this).attr('data-uri') == predicate.uri and
          ($(this).attr('data-inverse') == 'true') == predicate.inverse)
        displayed = true
  )

  # Predicate is not currently displayed
  return displayed


is_predicate_already_in_data_structure = (predicate) ->
  # Iterate through all predicates in the data structure
  for candidate in $('body').data('predicates')
    if (candidate['uri'] == predicate['uri'] and
        candidate['inverse'] == predicate['inverse'])
      return true

  # Predicate is not currently in the data structure
  return false


prepare_data_and_add_to_cells = (data) ->
  # Iterate through the objects
  for row in data.objects

    # If the object is a URI with a label, add the enclosing HTML
    if row.o.uri and row.o.label
      focus_filter_label = $("""td[data-s="#{row.s}"]""").first().text().trim()
      focus_url = "/search#?p0=http%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23label&p0i=false&p0ft=search&p0fv=#{encodeURIComponent(row.o.label).toLowerCase()}"
      focus_url += "&p1=http%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23type&p1i=false"
      focus_url += "&p2=#{encodeURIComponent(data.predicate['uri'])}&p2i=#{!data.predicate['inverse']}&p2ft=uri&p2fv=#{row.s}&p2fl=#{encodeURIComponent(focus_filter_label)}"
      focus_url += "&endpoint=#{$('body').data('endpoint')}&searchtype=#{$('body').data('search_type')}"

      row.o.html = """
      <div class="dropdown">
        <button type="button" class="btn btn-default btn-xs dropdown-toggle"
        data-toggle="dropdown" data-uri="#{row.o.uri}">
          #{row.o.label} <span class="caret"></span>
        </button>
        <ul class="dropdown-menu">
          <li>
            <a href="#" class="add_uri_filter">
              <span class="glyphicon glyphicon-filter"></span>
              Use <em>#{row.o.label}</em> as filter
            </a>
          </li>
          <li>
            <a href="#{focus_url}" target="_blank">
              <span class="glyphicon glyphicon-record"></span>
              Focus on <em>#{row.o.label}</em> (experimental)
            </a>
          </li>
          <li>
            <a href="#{row.o.uri}" target="_blank">
              <span class="glyphicon glyphicon-globe"></span>
              Open in Browser
            </a>
          </li>
        </ul>
      </div>
      """

    # Transform DBpedia's scientific notation into numbers
    # that people can actually read
    if (not row.o.uri and
        '.' in row.o.label and
        'e' in row.o.label.toLowerCase())
      row.o.html = parseFloat(row.o.label)

    # Make sure the object has a HTML representation
    if not row.o.html
      row.o.html = "<p>" + row.o.label + "</p>"

    # Highlight search terms
    if get_search_filter_for_predicate(data.predicate)

      filter_value = get_search_filter_for_predicate(data.predicate)
      filter_value_split = filter_value.split(' ')

      for value in filter_value_split
        regex = new RegExp(value, "ig")
        row.o.html = row.o.html.replace(regex, '<strong>$&</strong>')

    # Make big numbers better readable
    if !isNaN(parseFloat(row.o.html)) && isFinite(row.o.html)
      # Split the number at the decimal point
      split_number = row.o.html.toString().split('.')
      # Add thousands separators to the integer part
      row.o.html = split_number[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",")
      # Add the decimal part, if there is one
      if split_number[1]?
        row.o.html = row.o.html + '.' + split_number[1]

  # Now that every object has a label, sort the array of objects
  data.objects = data.objects.sort(
    (a, b) ->
      if (a.o.label > b.o.label)
        return 1
      if (a.o.label < b.o.label)
        return -1
      # a is equal to b
      return 0
  )

  # Iterate through the objects again
  for row in data.objects
    # Add the data to the table
    $("""td[data-s="#{row.s}"][data-p="#{data.predicate['uri']}"][data-inverse="#{data.predicate['inverse']}"]""")
      .append("#{row.o.html}\n")


set_cube_column_types = (data) ->
  # Get the index for the current column (predicate)
  predicate_index = \
    $("""th[data-uri="#{data.predicate['uri']}"]""").prevAll("th").length

  if not $('body').data('predicates')[predicate_index]
    debug 'ERROR: Trying to find the predicate in the table. Failing.'
    return

  # Check if the column is a dimension
  if data.predicate['uri'] of $('body').data('dimensions')
    # Update the data structure
    $('body').data('predicates')[predicate_index]['cube_component_type'] = \
      'dimension'
    # Add the info to the header cell
    if $("""#results tr:first th[data-uri="#{data.predicate['uri']}"] ul .defined_dimension""").length is 0
      $("""#results tr:first th[data-uri="#{data.predicate['uri']}"] ul""").append(
        """
        <li class="dimension" style="font-weight: normal;">
          <a class="cube_info defined_dimension" href="#">
            <span class="glyphicon glyphicon-info-sign"></span>
            This is by definition a cube dimension.
          </a>
        </li>
        """
      )
      $("""#results tr:first th[data-uri="#{data.predicate['uri']}"] ul""").prepend(
        """
        <li style="font-weight: normal;">
          <a class="group_by_column" href="#">
            <span class="glyphicon glyphicon-th-list"></span> Group by
            #{$('body').data('dimensions')[data.predicate['uri']]['label']}
          </a>
        </li>
        """
      )
    # Set the cube component type to 'dimension'
    $("th[data-uri='#{data.predicate['uri']}']")
      .attr('data-component', 'dimension')
    $("td[data-p='#{data.predicate['uri']}']")
      .attr('data-component', 'dimension')
      .attr(
        'data-range', 'http://code-research.eu/resource#CubeDimensionNominal'
      )
      .addClass('dimension')
      .removeClass('measure')

  # Check if the column is a measure
  else if data.predicate['uri'] of $('body').data('measures')
    # Update the data structure
    $('body').data('predicates')[predicate_index]['cube_component_type'] = \
      'measure'
    # Add the info to the header cell
    if $("""#results tr:first th[data-uri="#{data.predicate['uri']}"] ul .defined_measure""").length is 0
      $("""#results tr:first th[data-uri="#{data.predicate['uri']}"] ul""").append(
        """
        <li class="measure" style="font-weight: normal;">
          <a class="cube_info defined_measure" href="#">
            <span class="glyphicon glyphicon-info-sign"></span>
            This is by definition a cube measure.
          </a>
        </li>
        """
      )
    # Set the cube component type to 'measure'
    $("th[data-uri='#{data.predicate['uri']}']")
      .attr('data-component', 'observation')
    $("td[data-p=\"#{data.predicate['uri']}\"]")
      .attr('data-component', 'observation')
      .attr(
        'data-range', 'http://code-research.eu/resource#CubeObservationNumber'
      )
      .addClass('measure')
      .removeClass('dimension')


shorten_uri = (uri) ->
  # It's a hash URI
  if "#" in uri
    split = uri.split("#")
    short_uri = split[split.length - 1]

  # It's a slash URI
  else if "/" in uri
    split = uri.split("/")
    short_uri = split[split.length - 1]

  # Make it look pretty
  short_uri = short_uri.charAt(0).toUpperCase() + short_uri.substring(1)

  return short_uri


update_the_address = () ->
  # Reset the address
  $.address.value('')

  if are_we_in_dataset_mode()
    $.address.parameter(
      "dataset", encodeURIComponent($('body').data('dataset'))
    )

  # URL parameters for predicates and filters
  for predicate, index in $('body').data('predicates')
    $.address.parameter("p#{index}", encodeURIComponent(predicate['uri']))
    if predicate['inverse']
      $.address.parameter("p#{index}i", predicate['inverse'])
    else
      $.address.parameter("p#{index}i", false)
    if predicate['filter_type'] and predicate['filter_value']
      $.address.parameter("p#{index}ft", predicate['filter_type'])
      $.address.parameter(
        "p#{index}fv", encodeURIComponent(predicate['filter_value'])
      )
      if predicate['filter_label']
        $.address.parameter(
          "p#{index}fl", encodeURIComponent(predicate['filter_label'])
        )

  # URL parameter for non-default SPARQL endpoint
  if $('body').data('endpoint') != 'code'
    $.address.parameter(
      "endpoint",
      encodeURIComponent($('body').data('endpoint'))
    )

  # URL parameter for non-default search type
  if $('body').data('search_type') != 'regex'
    $.address.parameter('searchtype', $('body').data('search_type'))

  # Tell the browser to update the address
  $.address.update()


log_sparql_query_runtime = (runtime, text, query) ->
  $('#sparql_log').prepend(
    """
    <div>
      <p>
        <a class="sparql_toggle" href="#" style="color: rgba(51,51,51,1);">
          <span class="arrow" style="color: #666;">
            <span class="glyphicon glyphicon-chevron-right"></span>
          </span>
          #{(new Date).toTimeString().substr(0,8)} –
          #{runtime.toFixed(2)}s #{text}
        </a>
      </p>
      <textarea readonly="readonly" style="display: none; width: 100%;
      height: 200px; margin: 5px 0 10px 0;">#{htmlEncode(query)}</textarea>
    </div>
    """
  )


htmlEncode = (value) ->
  return $('<div/>').text(value).html()



###
Helper Functions - UI
###

ui_clear_spinner = () ->
  Spinners.get('#results_container').remove()


ui_display_front_page_alert = (message) ->
  $('#front_page .alert_container').append("""
    <div class="alert alert-warning">
      <button type="button" class="close" data-dismiss="alert">&times;</button>
      #{message}
    </div>
  """)


ui_display_results_page_alert = (message) ->
  $('#results_page .alert_container').append("""
    <div class="alert alert-warning">
      <button type="button" class="close" data-dismiss="alert">&times;</button>
      #{message}
    </div>
  """)


ui_display_the_front_page = () ->
  $('#results_page').hide()

  $('.alert_container').html('')
  $('#front_page').show()
  $('#q').select()

  get_and_display_the_datasets_of_the_selected_endpoint()


ui_display_the_results_page = () ->
  $('#front_page').hide()

  if are_we_in_dataset_mode()
    $('#results_page').attr('class', 'dataset')
  else
    $('#results_page').attr('class', 'generic')

  $('.alert_container').html('')
  $('#results_page').show()


ui_get_and_display_the_total_results_count = () ->
  return $.ajax({
    url: '/query/get_subjects_count',
    type: 'POST',
    data: JSON.stringify({
      endpoint_url: $('body').data('endpoint'),
      search_type: $('body').data('search_type'),
      predicates: $('body').data('predicates'),
      dataset: $('body').data('dataset')
    })
  })
  .done(
    (data) ->
      $('body').data('total_results_count', data['subjects_count'])
      $('#total_results_count').html(data['subjects_count'])
      ui_update_the_results_count()
      $('#results_count').show()

      # SPARQL performance
      log_sparql_query_runtime(
        data['runtime'],
        'for getting the subjects count',
        data['query'],
      )
  )


ui_display_spinner = () ->
  Spinners
    .create(
      '#results_container',
      {
        radius: 20,
        dashes: 18,
        width: 5,
        height: 20,
        opacity: .3,
        padding: 20,
        rotation: 600,
        color: '#000000'
      }
    )
    .play()


ui_update_the_load_more_results_area = (number_of_received_subjects) ->
  # There are probably more results available
  if parseInt(number_of_received_subjects) is $('body').data('BATCH_SIZE')

    amount_loadable_results = \
      $('body').data('total_results_count') - $('body').data('subjects').length

    $('div#load_more').html('')

    if amount_loadable_results > $('body').data('BATCH_SIZE')
      $('div#load_more').append(
        """
          <button class='btn btn-default' id='load_small' type='button'
          data-amount='#{$('body').data('BATCH_SIZE')}'>
            Load #{$('body').data('BATCH_SIZE')} more results
          </button>
        """
      )

    if amount_loadable_results > $('body').data('BIG_LOAD_SIZE')
      $('div#load_more').append(
        """
          <button class='btn btn-default' id='load_big' type='button'
          data-amount='#{$('body').data('BIG_LOAD_SIZE')}'>
            Load #{$('body').data('BIG_LOAD_SIZE')} more results
          </button>
        """
      )

    else if amount_loadable_results > 0
      $('div#load_more').append(
        """
          <button class='btn btn-default' id='load_all' type='button'
          data-amount='#{amount_loadable_results}'>
            Load all results
          </button>
        """
      )

  # We received less than BATCH_SIZE results
  else
    $('div#load_more').html('')

  # Spinner cleanup
  Spinners.removeDetached()


ui_update_the_results_count = () ->
  $('.current_results_count').each(
    () ->
      $(this).html($('body').data('subjects').length)
  )
