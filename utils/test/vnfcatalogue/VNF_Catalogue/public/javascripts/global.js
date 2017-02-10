/*******************************************************************************
 * Copyright (c) 2017 Kumar Rishabh and others.
 *
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Apache License, Version 2.0
 * which accompanies this distribution, and is available at
 * http://www.apache.org/licenses/LICENSE-2.0
 *******************************************************************************/

$(document).ready( function() {
    $('#Search').click(function() {
        var tags = $('#Tags').val().toLowerCase().split(/[ ,]+/);
        window.location.href = '/search_projects?tags=' + tags;
        return false;
    });
});
