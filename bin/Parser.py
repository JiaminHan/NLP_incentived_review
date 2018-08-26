def review_parser_new(review):
    # Reference variables
    agg = dict()
    fields = ['AuthorId','IsFeatured','IsRatingsOnly','IsRecommended', 'Rating', 'Title','ReviewText',
              'ContextDataValues.StaffContext.Value','ContextDataValues.IncentivizedReview.Value',
              'ContextDataValues.age.Value','ContextDataValues.beautyInsider.Value','Helpfulness','product_id',
             'productPrice','']
    for field in fields:
        value = review.get(field, None)
        #value = product.__dict__.get(field, None)

        try:
            agg[field] = value
            #agg[field] = unicode(value).encode('ascii', errors='ignore') if value is not None else None

        except:
            agg[field] = None
    return agg