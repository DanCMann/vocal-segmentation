procedure write_boundaries_to_csv: .textgrid, .outfile$
    writeFileLine: .outfile$, "label", ",", "start_boundary", ",", "end_boundary"
    selectObject: .textgrid
    n_tiers = Get number of tiers
    for i_tier from 1 to n_tiers

        tiername$ = Get tier name: i_tier
        if tiername$ = "segmentation"

            n_intervals = Get number of intervals: i_tier
            for i_interval from 1 to n_intervals
                interval_label$ = Get label of interval: i_tier, i_interval
                if interval_label$ = ""
                    #pass
                else
                    start = Get start point: i_tier, i_interval
                    end = Get end point: i_tier, i_interval
                    appendFileLine: .outfile$, interval_label$, ",", start, ",", end
                endif
            endfor
        endif
    endfor
endproc