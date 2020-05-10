package io.oisin.fyp;

import android.content.Context;
import android.content.res.Configuration;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;

import io.oisin.fyp.model.Direction;

/**
 * RecyclerView for displaying a list of directions of unknown length
 * Based off this guide: https://developer.android.com/guide/topics/ui/layout/recyclerview
 */
public class DirectionsAdapter extends
        RecyclerView.Adapter<DirectionsAdapter.ViewHolder> {

    private List<Direction> directions;
    private Context context;

    DirectionsAdapter(List<Direction> directions, Context context) {
        this.directions = directions;
        this.context = context;
    }

    @NonNull
    @Override
    public DirectionsAdapter.ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        Context context = parent.getContext();
        LayoutInflater inflater = LayoutInflater.from(context);

        View contactView = inflater.inflate(R.layout.item_direction, parent, false);

        return new ViewHolder(contactView);
    }

    @Override
    public void onBindViewHolder(DirectionsAdapter.ViewHolder viewHolder, int position) {
        Direction direction = directions.get(position);

        String directionString = direction.getDirection();
        String title = directionString.substring(0, 1).toUpperCase() + directionString.substring(1) + " on " + direction.getName();

        viewHolder.directionTitleTextView.setText(title);

        viewHolder.directionArrow.setImageResource(getResourceForArrow(directionString));

        if (direction.getDistance() < 0 && direction.getTime() < 0) {
            return;
        }

        if (direction.getDistance() < 95) {
            int distance = (int) Math.round(direction.getDistance()/10.0) * 10;

            viewHolder.directionSubtitleTextView.setText(distance + "m");
        } else {
            int distance = (int) Math.round(direction.getDistance()/100.0) * 100;

            viewHolder.directionSubtitleTextView.setText(distance + "m");
        }
    }

    private int getResourceForArrow(String direction) {
        int nightModeFlags =
                context.getResources().getConfiguration().uiMode &
                        Configuration.UI_MODE_NIGHT_MASK;
        if (nightModeFlags == Configuration.UI_MODE_NIGHT_NO) {
            switch (direction) {
                case "bear right":
                    return R.drawable.bear_right_arrow;
                case "bear left":
                    return R.drawable.bear_left_arrow;
                case "turn right":
                case "sharp right":
                    return R.drawable.right_arrow;
                case "turn left":
                case "sharp left":
                    return R.drawable.left_arrow;
                case "straight on":
                    return R.drawable.straight_ahead_arrow;
                case "grab a bike":
                    return R.drawable.bike_rack;
                case "leave your bike":
                    return R.drawable.empty_bike_rack;
            }

            return R.drawable.straight_ahead_arrow;
        } else {
            switch (direction) {
                case "bear right":
                    return R.drawable.bear_right_arrow_white;
                case "bear left":
                    return R.drawable.bear_left_arrow_white;
                case "turn right":
                case "sharp right":
                    return R.drawable.right_arrow_white;
                case "turn left":
                case "sharp left":
                    return R.drawable.left_arrow_white;
                case "straight on":
                    return R.drawable.straight_ahead_arrow_white;
                case "grab a bike":
                    return R.drawable.bike_rack_white;
                case "leave your bike":
                    return R.drawable.empty_bike_rack_white;
            }

            return R.drawable.straight_ahead_arrow_white;
        }
    }

    @Override
    public int getItemCount() {
        return directions.size();
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        TextView directionTitleTextView;
        TextView directionSubtitleTextView;
        ImageView directionArrow;

        ViewHolder(View itemView) {
            super(itemView);

            directionTitleTextView = itemView.findViewById(R.id.direction_title);
            directionSubtitleTextView = itemView.findViewById(R.id.direction_subtitle);
            directionArrow = itemView.findViewById(R.id.direction_arrow);
        }
    }
}